# **Author**: Tabish Hamid
# **Date**: 2025-09-27  
# **Description**: CSS styles and styling functions for the Streamlit app.

import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem;
        }
        
        .model-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #4ecdc4;
        }
        
        .winner-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .score-badge {
            background: #28a745;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 15px;
            font-weight: bold;
        }
        
        .provider-badge {
            padding: 0.2rem 0.4rem;
            border-radius: 10px;
            font-size: 0.8rem;
            color: white;
            margin-left: 0.5rem;
        }
        
        .groq-badge {
            background: #ff6b6b;
        }
        
        .ollama-badge {
            background: #6f42c1;
        }
        
        /* Additional utility styles */
        .metric-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.25rem 0;
            border: 1px solid #e9ecef;
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 0.75rem;
            border-radius: 0.375rem;
            border: 1px solid #f5c6cb;
            margin: 0.5rem 0;
        }
        
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 0.75rem;
            border-radius: 0.375rem;
            border: 1px solid #c3e6cb;
            margin: 0.5rem 0;
        }
        
        .info-message {
            background: #d1ecf1;
            color: #0c5460;
            padding: 0.75rem;
            border-radius: 0.375rem;
            border: 1px solid #bee5eb;
            margin: 0.5rem 0;
        }
        
        .warning-message {
            background: #fff3cd;
            color: #856404;
            padding: 0.75rem;
            border-radius: 0.375rem;
            border: 1px solid #ffeaa7;
            margin: 0.5rem 0;
        }
        
        /* Response display styling */
        .response-container {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #4ecdc4;
            margin: 1rem 0;
        }
        
        .response-meta {
            font-size: 0.875rem;
            color: #6c757d;
            margin-bottom: 0.5rem;
        }
        
        .response-text {
            line-height: 1.6;
            color: #212529;
        }
        
        /* Configuration styling */
        .config-section {
            border: 1px solid #dee2e6;
            border-radius: 0.375rem;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .config-header {
            font-weight: 600;
            color: #495057;
            margin-bottom: 0.5rem;
        }
        
        /* Progress styling */
        .progress-text {
            text-align: center;
            font-weight: 500;
            color: #495057;
            margin: 0.5rem 0;
        }
        
        /* Tab styling improvements */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 4px 4px 0 0;
            color: #495057;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #4ecdc4 !important;
            color: white !important;
        }
        
        /* Sidebar styling */
        .sidebar-section {
            margin-bottom: 1.5rem;
        }
        
        .sidebar-header {
            color: #495057;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        
        /* Button styling improvements */
        .stButton > button {
            border-radius: 0.375rem;
            border: 1px solid transparent;
            font-weight: 500;
            transition: all 0.15s ease-in-out;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Download button styling */
        .download-section {
            background: #f8f9fa;
            border-radius: 0.375rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Chart styling */
        .plotly-chart {
            border-radius: 0.375rem;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Dataframe styling */
        .dataframe {
            border-radius: 0.375rem;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Loading spinner customization */
        .stSpinner > div {
            border-top-color: #4ecdc4 !important;
        }
        
        /* Custom scrollbar for long responses */
        .response-text::-webkit-scrollbar {
            width: 6px;
        }
        
        .response-text::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }
        
        .response-text::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }
        
        .response-text::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .main-header {
                font-size: 1.75rem;
            }
            
            .winner-card {
                padding: 1rem;
            }
            
            .response-container {
                padding: 0.75rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def create_styled_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """Create a styled metric card"""
    delta_html = f'<p class="metric-delta">{delta}</p>' if delta else ""
    help_html = f'<small class="metric-help">{help_text}</small>' if help_text else ""
    
    return f"""
    <div class="metric-card">
        <h4 class="metric-title">{title}</h4>
        <p class="metric-value">{value}</p>
        {delta_html}
        {help_html}
    </div>
    """

def create_status_message(message: str, status_type: str = "info"):
    """Create a styled status message"""
    css_class = f"{status_type}-message"
    return f'<div class="{css_class}">{message}</div>'

def create_provider_badge(provider: str) -> str:
    """Create a styled provider badge"""
    if provider.lower() == "groq":
        return '<span class="provider-badge groq-badge">Groq</span>'
    elif provider.lower() == "ollama":
        return '<span class="provider-badge ollama-badge">Ollama</span>'
    else:
        return f'<span class="provider-badge">{provider}</span>'

def create_score_badge(score: float) -> str:
    """Create a styled score badge"""
    color = "#28a745" if score > 0.7 else "#ffc107" if score > 0.5 else "#dc3545"
    return f'<span class="score-badge" style="background: {color}">Score: {score:.3f}</span>'