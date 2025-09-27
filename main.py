# **Author**: Tabish Hamid
# **Date**: 2025-09-27
# **Description**: Streamlit app for comparing AI model responses from Groq Cloud and Ollama Local.


import streamlit as st
import asyncio
from datetime import datetime
import pandas as pd

from config.settings import PAGE_CONFIG, GROQ_MODELS, ERROR_MESSAGES
from models.groq_agent import GroqModelAgent
from models.ollama_agent import OllamaModelAgent
from utils.processing import process_query_multimodel
from utils.visualization import display_results
from ui.components import (
    show_provider_selection, show_model_configuration,
    show_example_queries, show_tips, show_current_configuration
)
from ui.styles import apply_custom_styles

def main():
    try:
        # Configure Streamlit page
        st.set_page_config(**PAGE_CONFIG)
        
        # Apply custom styling
        apply_custom_styles()
        
        # Header
        st.markdown('<div class="main-header">🤖 Multi-Provider AI Scoring System</div>', 
                    unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="font-size: 1.2rem; color: #666;">
                Compare responses from Groq Cloud ☁️ and Ollama Local 🏠 models • Cross-provider evaluation • Best answer wins
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar Configuration
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Provider selection
            provider_option = show_provider_selection()
            
            st.markdown("---")
            
            # Model configuration based on selection
            model_configs = show_model_configuration(provider_option)
            
            if not model_configs:
                return
            
            st.markdown("---")
            
            # Tips section
            with st.expander("💡 How it works"):
                st.markdown("""
                1. **Multi-Provider**: Compare cloud vs local models
                2. **Cross-Evaluation**: Each model scores all responses
                3. **Fair Comparison**: Normalized scoring across providers
                4. **Best Selection**: Highest-scoring response wins
                5. **Detailed Analysis**: View all responses and breakdowns
                """)
        
        # Main content area
        st.markdown("### 💬 Your Question")
        
        # Use example query if selected
        default_query = st.session_state.get('example_query', '')
        
        query = st.text_area(
            "Enter your question here:",
            value=default_query,
            placeholder="e.g., Explain quantum computing and its potential applications...",
            height=100,
            help="Ask anything! The models will compete to give you the best answer."
        )
        
        # Clear example after use
        if 'example_query' in st.session_state:
            del st.session_state.example_query
        
        # Process button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            process_button = st.button(
                "🚀 Compare Models", 
                type="primary",
                use_container_width=True
            )
        
        # Show current configuration
        if model_configs:
            show_current_configuration(model_configs)
        
        # Process the query
        if process_button and query.strip():
            if len(query.strip()) < 10:
                st.error("Please enter a more detailed question (at least 10 characters)")
                return
                
            st.markdown("---")
            
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Run the async process
                with st.spinner("Processing with multiple providers..."):
                    results = asyncio.run(process_query_multimodel(
                        query, model_configs, progress_bar, status_text
                    ))
                
                if results:
                    display_results(results, model_configs)
                else:
                    st.error("❌ No results generated")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                error_str = str(e)
                if "401" in error_str or "unauthorized" in error_str.lower():
                    st.error("🔑 Invalid Groq API key. Please check your key.")
                elif "429" in error_str or "rate limit" in error_str.lower():
                    st.error("⏰ Groq rate limit exceeded. Please wait and try again.")
                elif "timeout" in error_str.lower():
                    st.error("⏱️ Request timed out. Models might be busy - try again.")
                elif "ollama" in error_str.lower():
                    st.error("🏠 Ollama connection issue. Make sure Ollama is running and models are loaded.")
                else:
                    st.info("💡 This might be due to API limits or network issues. Please try again.")
                
                # Show troubleshooting tips
                with st.expander("🔧 Troubleshooting Tips"):
                    show_tips()
        
        # Show tips and examples when not processing
        elif not query.strip():
            col1, col2 = st.columns([1, 1])
            
            with col1:
                show_tips()
            
            with col2:
                example = show_example_queries()
                if example:
                    st.session_state.example_query = example
    
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page and try again.")

if __name__ == "__main__":
    main()