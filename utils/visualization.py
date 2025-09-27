# **Author**: Tabish Hamid
# **Date**: 2025-09-27
# **Description**: Visualization and display utilities.

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any

from config.settings import PROVIDER_COLORS
from utils.processing import prepare_results_for_export, create_summary_text

def display_results(results: Dict[str, Any], model_configs: List[Dict]):
    """Display the results in an attractive format"""
    
    try:
        best_response = results["best_response"]
        if not best_response or not hasattr(best_response, 'model_name'):
            st.error("❌ Invalid best response object")
            return
            
        if not results["ranking"]:
            st.error("❌ No ranking data available")
            return
            
        best_score = results["ranking"][0][1]["average_score"]
        
        # Display winner card
        _display_winner_card(best_response, best_score)
        
        # Scoring visualization
        st.markdown("### 📊 Scoring Results")
        fig = create_scoring_chart(results["ranking"], results["aggregated_scores"])
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed scoring matrix
        st.markdown("### 🎯 Detailed Scoring Matrix")
        model_names = [config["model_name"] for config in model_configs]
        scoring_df = create_scoring_matrix(results["all_scores"], model_names)
        st.dataframe(scoring_df, use_container_width=True)
        
        # All responses with provider badges
        _display_all_responses(results)
        
        # Download options
        _display_download_options(results)
            
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        if results:
            st.write("Debug - Results keys:", list(results.keys()))

def _display_winner_card(best_response, best_score):
    """Display the winner card"""
    # Get provider info for winner
    provider_badge = ""
    if "(Groq)" in best_response.model_name:
        provider_badge = '<span class="provider-badge groq-badge">Groq</span>'
    elif "(Ollama)" in best_response.model_name:
        provider_badge = '<span class="provider-badge ollama-badge">Ollama</span>'
    
    st.markdown(f"""
    <div class="winner-card">
        <h2 style="margin: 0; text-align: center;">🏆 Winner: {best_response.model_name.split(' (')[0]}{provider_badge}</h2>
        <p style="text-align: center; margin: 0.5rem 0;">
            <span class="score-badge">Score: {best_score:.3f}</span>
        </p>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <h4 style="margin-top: 0;">Best Response:</h4>
            <p style="margin-bottom: 0;">{best_response.response_text}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _display_all_responses(results):
    """Display all model responses in tabs"""
    st.markdown("### 📝 All Model Responses")
    
    model_names_from_responses = [r.model_name for r in results["responses"] if hasattr(r, 'model_name')]
    tab_names = []
    for name in model_names_from_responses:
        clean_name = name.split(' (')[0]
        if "(Groq)" in name:
            tab_names.append(f"🌐 {clean_name}")
        elif "(Ollama)" in name:
            tab_names.append(f"🏠 {clean_name}")
        else:
            tab_names.append(f"🤖 {clean_name}")
    
    tabs = st.tabs(tab_names)
    
    for i, (tab, response) in enumerate(zip(tabs, results["responses"])):
        with tab:
            if hasattr(response, 'model_name') and response.model_name in results["aggregated_scores"]:
                model_score = results["aggregated_scores"][response.model_name]["average_score"]
                individual_scores = results["aggregated_scores"][response.model_name]["individual_scores"]
                
                # Model info card with provider info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Overall Score", f"{model_score:.3f}")
                with col2:
                    confidence = getattr(response, 'confidence', 0.0)
                    st.metric("Confidence", f"{confidence:.3f}")
                with col3:
                    rank = next((idx for idx, (name, _) in enumerate(results["ranking"], 1) 
                               if name == response.model_name), "N/A")
                    st.metric("Rank", f"#{rank}")
                with col4:
                    provider = "Groq" if "(Groq)" in response.model_name else "Ollama" if "(Ollama)" in response.model_name else "Unknown"
                    st.metric("Provider", provider)
                
                # Individual scores from each evaluator
                st.markdown("**Scores from each evaluator:**")
                if individual_scores and len(individual_scores) >= len(model_names_from_responses):
                    score_cols = st.columns(len(individual_scores))
                    for j, (col, score) in enumerate(zip(score_cols, individual_scores)):
                        evaluator_name = model_names_from_responses[j].split(' (')[0] if j < len(model_names_from_responses) else f"Evaluator {j+1}"
                        with col:
                            color = "🟢" if score > 0.7 else "🟡" if score > 0.5 else "🔴"
                            st.write(f"{color} **{evaluator_name}**: {score:.3f}")
                else:
                    st.write("Individual scoring data incomplete")
            
            # Response text
            st.markdown("**Response:**")
            response_text = getattr(response, 'response_text', 'No response text available')
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #4ecdc4;">
                {response_text}
            </div>
            """, unsafe_allow_html=True)

def _display_download_options(results):
    """Display download options"""
    st.markdown("---")
    st.markdown("### 💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        results_json = prepare_results_for_export(results)
        st.download_button(
            label="📥 Download Full Results (JSON)",
            data=json.dumps(results_json, indent=2, default=str),
            file_name=f"ai_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        summary_text = create_summary_text(results)
        st.download_button(
            label="📄 Download Summary (TXT)",
            data=summary_text,
            file_name=f"ai_comparison_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

def create_scoring_chart(ranking: List, aggregated_scores: Dict) -> go.Figure:
    """Create a bar chart showing model scores"""
    
    if not ranking:
        fig = go.Figure()
        fig.update_layout(title="No scoring data available")
        return fig
    
    models = [item[0].split(' (')[0] for item in ranking]  # Clean model names
    scores = [item[1]["average_score"] for item in ranking]
    providers = ["Groq" if "(Groq)" in item[0] else "Ollama" if "(Ollama)" in item[0] else "Unknown" for item in ranking]
    
    # Color by provider
    colors = []
    for provider in providers:
        if provider == "Groq":
            colors.append(PROVIDER_COLORS["groq"])
        elif provider == "Ollama":
            colors.append(PROVIDER_COLORS["ollama"])
        else:
            colors.append(PROVIDER_COLORS["unknown"])
    
    # Make winner gold
    colors[0] = PROVIDER_COLORS["winner"]
    
    fig = go.Figure(data=[
        go.Bar(
            x=models,
            y=scores,
            marker_color=colors,
            text=[f"{score:.3f}" for score in scores],
            textposition='auto',
            name="Average Score",
            hovertemplate='<b>%{x}</b><br>Score: %{y:.3f}<br>Provider: %{customdata}<extra></extra>',
            customdata=providers
        )
    ])
    
    fig.update_layout(
        title="🏆 Model Performance Ranking",
        xaxis_title="Models",
        yaxis_title="Average Score",
        yaxis=dict(range=[0, 1.0]),
        height=400,
        showlegend=False
    )
    
    return fig

def create_scoring_matrix(all_scores: List, model_configs: List[Dict]) -> pd.DataFrame:
    """Create a scoring matrix DataFrame"""
    
    matrix_data = []
    
    try:
        for i, config in enumerate(model_configs):
            if isinstance(config, Dict):
                evaluator_name = f"{config['model_name']} ({config['provider'].title()})"
            else:
                evaluator_name = str(config)
            row = {"Evaluator": evaluator_name}
            
            if i < len(all_scores):
                evaluator_scores = all_scores[i]
                
                for score_result in evaluator_scores:
                    if hasattr(score_result, 'target_model') and hasattr(score_result, 'score'):
                        target_model = score_result.target_model.split(' (')[0]  # Clean name
                        row[f"→ {target_model}"] = f"{score_result.score:.3f}"
            
            matrix_data.append(row)
        
        df = pd.DataFrame(matrix_data)
        return df
        
    except Exception as e:
        return pd.DataFrame([{"Error": f"Could not create scoring matrix: {str(e)}"}])
