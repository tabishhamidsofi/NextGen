# **Author**: Tabish Hamid
# **Date**: 2025-09-27
# **Description**: Base classes and data models for the Multi-Agent Scoring System.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
from config.settings import CONFIDENCE_WORDS, UNCERTAINTY_WORDS

@dataclass
class ModelResponse:
    """Data class representing a model's response"""
    model_name: str
    response_text: str
    confidence: float
    reasoning: str
    timestamp: datetime

@dataclass 
class ScoringResult:
    """Data class representing the scoring of a response"""
    evaluator_model: str
    target_model: str
    score: float
    reasoning: str
    criteria_scores: Dict[str, float]

class BaseModelAgent(ABC):
    """Abstract base class for all model agents"""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.model_type = self._get_model_type()
    
    @abstractmethod
    async def generate_response(self, query: str) -> ModelResponse:
        """Generate a response to the given query"""
        pass
    
    @abstractmethod
    async def score_response(self, query: str, response: ModelResponse) -> ScoringResult:
        """Score a response from another model"""
        pass
    
    @abstractmethod
    def _get_model_type(self) -> str:
        """Return the model type (groq, ollama, etc.)"""
        pass
    
    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate confidence based on text content
        
        Args:
            text: The response text to analyze
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        if not text or len(text.strip()) == 0:
            return 0.0
        
        if text.startswith("❌"):
            return 0.0
            
        confidence_words = len([w for w in CONFIDENCE_WORDS if w in text.lower()])
        uncertainty_words = len([w for w in UNCERTAINTY_WORDS if w in text.lower()])
        
        base_confidence = 0.7
        confidence_boost = confidence_words * 0.05
        confidence_penalty = uncertainty_words * 0.1
        
        return max(0.1, min(1.0, base_confidence + confidence_boost - confidence_penalty))
    
    def create_error_response(self, error_message: str, reasoning: str = "Error occurred") -> ModelResponse:
        """
        Create a standardized error response
        
        Args:
            error_message: The error message to include
            reasoning: The reason for the error
            
        Returns:
            ModelResponse: An error response object
        """
        return ModelResponse(
            model_name=f"{self.model_name} ({self.model_type.title()})",
            response_text=f"❌ {error_message}",
            confidence=0.0,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
    
    def create_error_scoring(self, target_model: str, error_message: str, score: float = 0.0) -> ScoringResult:
        """
        Create a standardized error scoring result
        
        Args:
            target_model: The model that was being scored
            error_message: The error message
            score: The score to assign (default 0.0)
            
        Returns:
            ScoringResult: An error scoring result
        """
        return ScoringResult(
            evaluator_model=f"{self.model_name} ({self.model_type.title()})",
            target_model=target_model,
            score=score,
            reasoning=error_message,
            criteria_scores={"overall": score}
        )

def create_model_agent(provider: str, model_name: str, **kwargs) -> BaseModelAgent:
    """
    Factory function to create model agents
    
    Args:
        provider: The provider type ('groq' or 'ollama')
        model_name: The name of the model
        **kwargs: Additional arguments for the specific agent
        
    Returns:
        BaseModelAgent: The created model agent
        
    Raises:
        ValueError: If the provider is unknown
    """
    if provider == "groq":
        from models.groq_agent import GroqModelAgent
        return GroqModelAgent(model_name, kwargs.get("api_key"))
    elif provider == "ollama":
        from models.ollama_agent import OllamaModelAgent
        return OllamaModelAgent(model_name, kwargs.get("base_url", "http://localhost:11434"))
    else:
        raise ValueError(f"Unknown provider: {provider}")