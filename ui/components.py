# **Author**: Tabish Hamid
# **Date**: 2025-09-27
# **Description**: Reusable UI components for the Streamlit app.

import streamlit as st
import asyncio
import pandas as pd
from typing import List, Dict, Optional

from config.settings import (
    PROVIDER_OPTIONS, GROQ_MODELS, DEFAULT_OLLAMA_URL, 
    EXAMPLE_QUERIES, MIN_MODELS_REQUIRED
)
from models.ollama_agent import get_ollama_models

def show_provider_selection() -> str:
    """Show provider selection UI"""
    st.subheader("🔌 Select Provider Mix")
    
    provider_option = st.radio(
        "Choose your setup:",
        PROVIDER_OPTIONS,
        help="Mixed mode gives best comparison between cloud and local models"
    )
    
    return provider_option

def show_model_configuration(provider_option: str) -> Optional[List[Dict]]:
    """
    Show model configuration UI based on provider selection
    
    Args:
        provider_option: The selected provider option
        
    Returns:
        List of model configurations or None if invalid
    """
    
    if provider_option == "Mixed (Groq + Ollama)":
        return _show_mixed_configuration()
    elif provider_option == "Groq Only":
        return _show_groq_only_configuration()
    elif provider_option == "Ollama Only":
        return _show_ollama_only_configuration()
    else:
        st.error("Unknown provider option")
        return None

def _show_mixed_configuration() -> Optional[List[Dict]]:
    """Show configuration for mixed Groq + Ollama setup"""
    st.markdown("### 🌐 Groq Configuration")
    
    api_key = st.text_input(
        "🔑 Groq API Key", 
        type="password",
        help="Get your API key from https://console.groq.com/"
    )
    
    groq_model = st.selectbox("Select Groq Model", GROQ_MODELS, index=0)
    
    st.markdown("### 🏠 Ollama Configuration")
    
    ollama_url = st.text_input(
        "🔗 Ollama URL", 
        value=DEFAULT_OLLAMA_URL,
        help="URL where Ollama is running"
    )
    
    # Fetch Ollama models
    ollama_models = _get_ollama_models_cached(ollama_url)
    
    if not ollama_models:
        st.error("❌ Could not connect to Ollama or no models found")
        st.markdown("""
        **To fix this:**
        1. Start Ollama: `ollama serve`
        2. Pull models: `ollama pull llama2`
        3. Click 'Refresh Ollama Models'
        """)
        return None
    else:
        st.success(f"✅ Found {len(ollama_models)} Ollama models")
    
    ollama_model1 = st.selectbox("Select Ollama Model 1", ollama_models, index=0)
    ollama_model2 = st.selectbox("Select Ollama Model 2", ollama_models, 
                               index=1 if len(ollama_models) > 1 else 0)
    
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key")
        return None
    
    if ollama_model1 == ollama_model2:
        st.warning("⚠️ Please select different Ollama models")
        return None
    
    return [
        {"provider": "groq", "model_name": groq_model, "api_key": api_key},
        {"provider": "ollama", "model_name": ollama_model1, "base_url": ollama_url},
        {"provider": "ollama", "model_name": ollama_model2, "base_url": ollama_url},
    ]

def _show_groq_only_configuration() -> Optional[List[Dict]]:
    """Show configuration for Groq only setup"""
    st.markdown("### 🌐 Groq Configuration")
    
    api_key = st.text_input(
        "🔑 Groq API Key", 
        type="password",
        help="Get your API key from https://console.groq.com/"
    )
    
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key")
        return None
    
    model1 = st.selectbox("Model 1", GROQ_MODELS, index=0)
    model2 = st.selectbox("Model 2", GROQ_MODELS, index=1)
    model3 = st.selectbox("Model 3", GROQ_MODELS, index=2)
    
    selected_models = [model1, model2, model3]
    
    if len(set(selected_models)) != 3:
        st.error("⚠️ Please select 3 different models")
        return None
    
    return [
        {"provider": "groq", "model_name": model, "api_key": api_key}
        for model in selected_models
    ]

def _show_ollama_only_configuration() -> Optional[List[Dict]]:
    """Show configuration for Ollama only setup"""
    st.markdown("### 🏠 Ollama Configuration")
    
    ollama_url = st.text_input(
        "🔗 Ollama URL", 
        value=DEFAULT_OLLAMA_URL,
        help="URL where Ollama is running"
    )
    
    ollama_models = _get_ollama_models_cached(ollama_url, key_suffix="only")
    
    if not ollama_models:
        st.error("❌ Could not connect to Ollama or no models found")
        st.markdown("""
        **To fix this:**
        1. Start Ollama: `ollama serve`
        2. Pull models: `ollama pull llama2`
        3. Click 'Refresh Ollama Models'
        """)
        return None
    else:
        st.success(f"✅ Found {len(ollama_models)} Ollama models")
    
    if len(ollama_models) < MIN_MODELS_REQUIRED:
        st.error(f"❌ Need at least {MIN_MODELS_REQUIRED} models for comparison")
        st.info("Pull more models: `ollama pull modelname`")
        return None
    
    model1 = st.selectbox("Model 1", ollama_models, index=0)
    model2 = st.selectbox("Model 2", ollama_models, index=1)
    model3 = st.selectbox("Model 3", ollama_models, index=2)
    
    selected_models = [model1, model2, model3]
    
    if len(set(selected_models)) != 3:
        st.error("⚠️ Please select 3 different models")
        return None
    
    return [
        {"provider": "ollama", "model_name": model, "base_url": ollama_url}
        for model in selected_models
    ]

def _get_ollama_models_cached(ollama_url: str, key_suffix: str = "") -> List[str]:
    """Get Ollama models with caching"""
    cache_key = f"ollama_models{key_suffix}"
    
    if st.button(f"🔄 Refresh Ollama Models", key=f"refresh_ollama{key_suffix}"):
        st.session_state[cache_key] = None
    
    if cache_key not in st.session_state or st.session_state[cache_key] is None:
        with st.spinner("Fetching Ollama models..."):
            st.session_state[cache_key] = asyncio.run(get_ollama_models(ollama_url))
    
    return st.session_state[cache_key]

def show_current_configuration(model_configs: List[Dict]):
    """Show the current model configuration"""
    st.markdown("### 🔧 Current Configuration")
    config_df = pd.DataFrame([
        {
            "Model": config["model_name"],
            "Provider": config["provider"].title(),
            "Type": "☁️ Cloud" if config["provider"] == "groq" else "🏠 Local"
        }
        for config in model_configs
    ])
    st.dataframe(config_df, use_container_width=True, hide_index=True)

def show_example_queries() -> Optional[str]:
    """Show example queries to inspire users"""
    
    st.markdown("### 💡 Example Queries to Try")
    
    for i, example in enumerate(EXAMPLE_QUERIES, 1):
        if st.button(f"💫 Try Example {i}", key=f"example_{i}", help=example):
            return example
    
    return None

def show_tips():
    """Show usage tips"""
    st.markdown("""
    ### 💡 Tips for Best Results
    
    - **Mix Providers**: Compare cloud (Groq) vs local (Ollama) models
    - **Ask specific questions**: More detailed queries get better responses
    - **Try different topics**: Test various domains (tech, science, philosophy, etc.)
    - **Compare model strengths**: Different models excel at different types of questions
    - **Use the scoring**: Pay attention to why models score each other differently
    - **Export results**: Save interesting comparisons for later reference
    
    ### ⚠️ Troubleshooting
    
    **Groq Issues:**
    - Check your API key and ensure you have credits
    - Rate limits: If you hit limits, wait before trying again
    
    **Ollama Issues:**
    - Make sure Ollama is running: `ollama serve`
    - Ensure models are pulled: `ollama pull llama2`
    - Check if models are loaded: `ollama list`
    - Local models may take longer to respond
    
    **General:**
    - Network issues: Refresh the page if connections fail
    - Mixed responses are normal - each provider has different strengths
    """)