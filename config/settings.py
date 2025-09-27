# **Author**: Tabish Hamid
# **Date**: 2025-09-27
# **Description**: Configuration settings and constants for the Multi-Agent Scoring System.


# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "🤖 Multi-Agent Scoring System",
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Groq API Configuration
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODELS = [
    "qwen/qwen3-32b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "openai/gpt-oss-20b",
    "moonshotai/kimi-k2-instruct-0905",
    "meta-llama/llama-4-scout-17b-16e-instruct",
]

# Ollama Configuration
DEFAULT_OLLAMA_URL = "http://localhost:11434"
OLLAMA_ENDPOINTS = {
    "generate": "/api/generate",
    "tags": "/api/tags"
}

# Request timeouts (in seconds)
TIMEOUTS = {
    "groq": 60,
    "ollama": 120,
    "ollama_models": 10
}

# Response generation parameters
GENERATION_PARAMS = {
    "groq": {
        "temperature": 0.7,
        "max_tokens": 1500
    },
    "ollama": {
        "temperature": 0.7,
        "num_predict": 1500
    }
}

# Scoring parameters
SCORING_PARAMS = {
    "groq": {
        "temperature": 0.3,
        "max_tokens": 500
    },
    "ollama": {
        "temperature": 0.3,
        "num_predict": 500
    }
}

# UI Configuration
PROVIDER_OPTIONS = [
    "Mixed (Groq + Ollama)", 
    "Groq Only", 
    "Ollama Only"
]

# Example queries for user inspiration
EXAMPLE_QUERIES = [
    "Explain quantum computing and its potential real-world applications",
    "What are the pros and cons of remote work for businesses and employees?", 
    "How will artificial intelligence change healthcare in the next 10 years?",
    "Compare renewable energy sources and their effectiveness",
    "Explain blockchain technology and its uses beyond cryptocurrency",
    "What are the ethical implications of gene editing technology?",
    "How can cities become more sustainable and environmentally friendly?",
    "Describe the future of transportation and autonomous vehicles"
]

# Error messages
ERROR_MESSAGES = {
    "invalid_api_key": "🔑 Invalid Groq API key. Please check your key.",
    "rate_limit": "⏰ Groq rate limit exceeded. Please wait and try again.",
    "timeout": "⏱️ Request timed out. Models might be busy - try again.",
    "ollama_connection": "🏠 Ollama connection issue. Make sure Ollama is running and models are loaded.",
    "generic": "💡 This might be due to API limits or network issues. Please try again."
}

# Scoring criteria and prompts
SCORING_PROMPT_TEMPLATE = """
Score this AI response on a scale of 0.0 to 1.0:

QUERY: {query}

RESPONSE: {response}

Rate on these criteria:
ACCURACY: [0.0-1.0]
COMPLETENESS: [0.0-1.0]
CLARITY: [0.0-1.0]
OVERALL: [0.0-1.0]
REASONING: [Brief explanation]

Provide your evaluation in the exact format above.
"""

# Confidence estimation words
CONFIDENCE_WORDS = ["certain", "confident", "clearly", "definitely", "obviously"]
UNCERTAINTY_WORDS = ["might", "possibly", "unclear", "maybe", "perhaps"]

# Chart colors by provider
PROVIDER_COLORS = {
    "groq": '#ff6b6b',
    "ollama": '#6f42c1',
    "unknown": '#78c2ad',
    "winner": '#FFD700'
}

# Minimum requirements
MIN_QUERY_LENGTH = 10
MIN_MODELS_REQUIRED = 3