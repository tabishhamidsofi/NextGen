# **Author**: Tabish Hamid
# **Date**: 2025-09-27
# **Description**: Core processing logic for multi-model comparison

import streamlit as st
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from models.base import BaseModelAgent, ModelResponse, create_model_agent

async def process_query_multimodel(
    query: str, 
    model_configs: List[Dict], 
    progress_bar, 
    status_text
) -> Optional[Dict[str, Any]]:
    """
    Process query with multiple model providers
    
    Args:
        query: The user's question
        model_configs: List of model configurations
        progress_bar: Streamlit progress bar
        status_text: Streamlit text element for status updates
        
    Returns:
        Dict containing all results and analysis
    """
    
    try:
        # Create agents
        agents = []
        for config in model_configs:
            agent = create_model_agent(**config)
            agents.append(agent)
        
        st.write(f"Created {len(agents)} agents from different providers")
        
        # Step 1: Generate responses
        status_text.text("🤔 Models are thinking... (Step 1/3)")
        progress_bar.progress(10)
        
        responses = await _generate_all_responses(agents, query)
        
        # Check if we have any valid responses
        valid_responses = [r for r in responses if not r.response_text.startswith("❌")]
        if len(valid_responses) == 0:
            raise Exception("All models failed to generate valid responses")
        
        progress_bar.progress(40)
        status_text.text("✅ All responses generated! Now scoring... (Step 2/3)")
        
        # Step 2: Score responses
        all_scores = await _score_all_responses(agents, query, responses, progress_bar)
        
        status_text.text("🏆 Determining winner... (Step 3/3)")
        progress_bar.progress(90)
        
        # Step 3: Aggregate scores and determine winner
        results = _aggregate_results(query, responses, all_scores, model_configs)
        
        progress_bar.progress(100)
        status_text.text("✨ Complete! Results ready.")
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return results
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Error in process_query_multimodel: {str(e)}")
        raise e

async def _generate_all_responses(agents: List[BaseModelAgent], query: str) -> List[ModelResponse]:
    """Generate responses from all agents"""
    responses = []
    
    for i, agent in enumerate(agents):
        st.write(f"Getting response from {agent.model_name} ({agent.model_type})...")
        response = await agent.generate_response(query)
        
        if isinstance(response, ModelResponse):
            responses.append(response)
            st.write(f"✅ Got response from {response.model_name}")
        else:
            st.write(f"❌ Invalid response type from {agent.model_name}")
            error_response = ModelResponse(
                model_name=f"{agent.model_name} ({agent.model_type})",
                response_text="❌ Failed to get valid response",
                confidence=0.0,
                reasoning="Invalid response type",
                timestamp=datetime.now()
            )
            responses.append(error_response)
    
    return responses

async def _score_all_responses(
    agents: List[BaseModelAgent], 
    query: str, 
    responses: List[ModelResponse], 
    progress_bar
) -> List[List]:
    """Score all responses using all agents"""
    all_scores = []
    
    for i, agent in enumerate(agents):
        st.write(f"Agent {agent.model_name} ({agent.model_type}) scoring all responses...")
        agent_scores = []
        
        for j, response in enumerate(responses):
            if isinstance(response, ModelResponse):
                score = await agent.score_response(query, response)
                agent_scores.append(score)
                st.write(f"  ✅ Scored {response.model_name}: {score.score}")
            else:
                st.write(f"  ❌ Skipping invalid response")
                default_score = agent.create_error_scoring(
                    f"model_{j}",
                    "Invalid response object"
                )
                agent_scores.append(default_score)
        
        all_scores.append(agent_scores)
        progress_bar.progress(40 + (i + 1) * 15)
    
    return all_scores

def _aggregate_results(
    query: str, 
    responses: List[ModelResponse], 
    all_scores: List[List], 
    model_configs: List[Dict]
) -> Dict[str, Any]:
    """Aggregate all results into final format"""
    
    # Calculate model scores
    model_scores = {}
    for response in responses:
        if isinstance(response, ModelResponse):
            model_scores[response.model_name] = []
    
    for agent_scores in all_scores:
        for score in agent_scores:
            if hasattr(score, 'target_model') and score.target_model in model_scores:
                model_scores[score.target_model].append(score.score)
    
    # Calculate averages
    aggregated_scores = {}
    for model_name, scores in model_scores.items():
        if scores:
            avg_score = sum(scores) / len(scores)
            aggregated_scores[model_name] = {
                "average_score": round(avg_score, 3),
                "individual_scores": scores
            }
        else:
            aggregated_scores[model_name] = {
                "average_score": 0.0,
                "individual_scores": []
            }
    
    # Create ranking
    ranking = sorted(aggregated_scores.items(), key=lambda x: x[1]["average_score"], reverse=True)
    
    # Find best response
    best_response = _find_best_response(ranking, responses)
    
    if best_response is None:
        raise Exception("Could not determine best response")
    
    return {
        "query": query,
        "responses": responses,
        "all_scores": all_scores,
        "aggregated_scores": aggregated_scores,
        "ranking": ranking,
        "best_response": best_response,
        "model_configs": model_configs
    }

def _find_best_response(ranking: List[tuple], responses: List[ModelResponse]) -> Optional[ModelResponse]:
    """Find the best response based on ranking"""
    if not ranking or not responses:
        return None
    
    best_model_name = ranking[0][0]
    
    # Try to find exact match
    for response in responses:
        if isinstance(response, ModelResponse) and response.model_name == best_model_name:
            return response
    
    # Fallback to first valid response
    for response in responses:
        if isinstance(response, ModelResponse):
            return response
    
    return None

def prepare_results_for_export(results: Dict) -> Dict:
    """Prepare results for JSON export"""
    try:
        export_data = {
            "query": results.get("query", ""),
            "timestamp": datetime.now().isoformat(),
            "models_compared": len(results.get("responses", [])),
            "winner": {},
            "full_ranking": [],
            "all_responses": [],
            "model_configs": results.get("model_configs", [])
        }
        
        if results.get("best_response") and hasattr(results["best_response"], 'model_name'):
            best_response = results["best_response"]
            winner_score = results["ranking"][0][1]["average_score"] if results.get("ranking") else 0
            export_data["winner"] = {
                "model": best_response.model_name,
                "score": winner_score,
                "response": getattr(best_response, 'response_text', '')
            }
        
        if results.get("ranking"):
            export_data["full_ranking"] = [
                {
                    "rank": i+1,
                    "model": model,
                    "score": data["average_score"],
                    "individual_scores": data["individual_scores"]
                }
                for i, (model, data) in enumerate(results["ranking"])
            ]
        
        if results.get("responses"):
            for response in results["responses"]:
                if hasattr(response, 'model_name'):
                    export_data["all_responses"].append({
                        "model": response.model_name,
                        "response": getattr(response, 'response_text', ''),
                        "confidence": getattr(response, 'confidence', 0.0),
                        "timestamp": getattr(response, 'timestamp', datetime.now()).isoformat()
                    })
        
        return export_data
    except Exception as e:
        return {"error": f"Could not prepare export data: {str(e)}"}

def create_summary_text(results: Dict) -> str:
    """Create a text summary of results"""
    
    try:
        summary = f"""
AI MODEL COMPARISON RESULTS (Multi-Provider)
===========================================
Query: {results.get("query", "Unknown")}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Models Compared: {len(results.get("responses", []))}
Providers: Groq, Ollama

WINNER:
"""
        
        if results.get("best_response") and hasattr(results["best_response"], 'model_name'):
            winner_score = results["ranking"][0][1]["average_score"] if results.get("ranking") else "N/A"
            summary += f"🏆 {results['best_response'].model_name}\n"
            summary += f"Score: {winner_score}\n"
        else:
            summary += "Unknown\n"

        summary += "\nFULL RANKING:\n"
        
        if results.get("ranking"):
            for i, (model, data) in enumerate(results["ranking"], 1):
                provider = "Groq" if "(Groq)" in model else "Ollama" if "(Ollama)" in model else "Unknown"
                clean_model = model.split(' (')[0]
                summary += f"{i}. {clean_model} ({provider}): {data['average_score']:.3f}\n"
        else:
            summary += "No ranking data available\n"
        
        if results.get("best_response") and hasattr(results["best_response"], 'response_text'):
            summary += f"\nBEST RESPONSE:\n{'-' * 40}\n{results['best_response'].response_text}\n\n"
        
        summary += "ALL RESPONSES:\n" + "=" * 50 + "\n"
        if results.get("responses"):
            for i, response in enumerate(results["responses"], 1):
                if hasattr(response, 'model_name'):
                    model_name = response.model_name
                    clean_name = model_name.split(' (')[0]
                    provider = "Groq" if "(Groq)" in model_name else "Ollama" if "(Ollama)" in model_name else "Unknown"
                    model_score = results.get("aggregated_scores", {}).get(model_name, {}).get("average_score", "N/A")
                    response_text = getattr(response, 'response_text', 'No response text')
                    
                    summary += f"\n{i}. {clean_name} ({provider}) - Score: {model_score}\n"
                    summary += f"{'-' * 40}\n{response_text}\n"
        else:
            summary += "No responses available\n"
        
        return summary
        
    except Exception as e:
        return f"Error creating summary: {str(e)}"