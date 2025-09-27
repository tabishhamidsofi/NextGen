# README.md
# Multi-Agent Scoring System

A comprehensive system for comparing AI model responses across different providers (Groq Cloud and Ollama Local).


## Features

- **Multi-Provider Support**: Compare cloud (Groq) and local (Ollama) models
- **Cross-Evaluation**: Each model scores all responses for fair comparison
- **Interactive UI**: Streamlit-based interface with real-time progress tracking
- **Comprehensive Analysis**: Detailed scoring matrices and visualizations
- **Export Options**: Download results in JSON or summary text format

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. For Groq: Get API key from https://console.groq.com/

3. For Ollama: Install and start Ollama service:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull models
ollama pull llama2
ollama pull mistral
```

## Usage

1. Run the application:
```bash
streamlit run main.py
```

2. Configure providers in the sidebar
3. Enter your question
4. Compare model responses and scoring

## Architecture Benefits

- **Modular Design**: Each component has a specific responsibility
- **Easy Testing**: Individual modules can be tested separately  
- **Maintainable**: Clean separation of concerns
- **Extensible**: Easy to add new providers or features
- **Reusable**: Components can be used in other projects

## Adding New Providers

1. Create new agent class inheriting from `BaseModelAgent`
2. Implement required methods (`generate_response`, `score_response`) 
3. Add provider to factory function in `models/base.py`
4. Update UI components to include new provider option
