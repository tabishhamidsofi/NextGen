# **Author**: Tabish Hamid
# **Date**: 2025-09-27
# **Description**: Ollama model agent implementation.

import aiohttp
import asyncio
import re
from datetime import datetime
from typing import List

from models.base import BaseModelAgent, ModelResponse, ScoringResult
from config.settings import (
    DEFAULT_OLLAMA_URL, OLLAMA_ENDPOINTS, TIMEOUTS, 
    GENERATION_PARAMS, SCORING_PARAMS, SCORING_PROMPT_TEMPLATE
)

class OllamaModelAgent(BaseModelAgent):
    """Agent for interacting with Ollama local models"""
    
    def __init__(self, model_name: str, base_url: str = DEFAULT_OLLAMA_URL):
        super().__init__(model_name)
        self.base_url = base_url.rstrip('/')
    
    def _get_model_type(self) -> str:
        return "ollama"
    
    async def generate_response(self, query: str) -> ModelResponse:
        """
        Generate a response from Ollama model
        
        Args:
            query: The user's question
            
        Returns:
            ModelResponse: The model's response or error
        """
        payload = {
            "model": self.model_name,
            "prompt": query,
            "stream": False,
            "options": GENERATION_PARAMS["ollama"]
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=TIMEOUTS["ollama"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}{OLLAMA_ENDPOINTS['generate']}",
                    json=payload
                ) as response:
                    return await self._process_generation_response(response)
                    
        except asyncio.TimeoutError:
            return self.create_error_response(
                "Ollama request timed out (model may not be loaded)", 
                "Timeout error"
            )
        except Exception as e:
            return self.create_error_response(
                f"Ollama connection failed: {str(e)}", 
                "Connection error"
            )
    
    async def _process_generation_response(self, response: aiohttp.ClientResponse) -> ModelResponse:
        """Process the response from Ollama generation API"""
        if response.status == 200:
            try:
                response_data = await response.json()
                response_text = response_data.get("response", "")
                
                if response_text:
                    return ModelResponse(
                        model_name=f"{self.model_name} (Ollama)",
                        response_text=response_text,
                        confidence=self._estimate_confidence(response_text),
                        reasoning="Ollama local response",
                        timestamp=datetime.now()
                    )
                else:
                    return self.create_error_response("Empty response from Ollama", "Empty response")
                    
            except (KeyError, ValueError) as e:
                return self.create_error_response(
                    f"Invalid Ollama response format: {str(e)}", 
                    "Response format error"
                )
        else:
            error_text = await response.text()
            return self.create_error_response(
                f"Ollama error {response.status}: {error_text[:200]}", 
                "Ollama API error"
            )
    
    async def score_response(self, query: str, response: ModelResponse) -> ScoringResult:
        """
        Score a response using Ollama model
        
        Args:
            query: The original question
            response: The response to score
            
        Returns:
            ScoringResult: The scoring result
        """
        if not isinstance(response, ModelResponse):
            return self.create_error_scoring(
                "unknown", 
                "Invalid response object for scoring"
            )
        
        scoring_prompt = SCORING_PROMPT_TEMPLATE.format(
            query=query, 
            response=response.response_text
        )
        
        payload = {
            "model": self.model_name,
            "prompt": scoring_prompt,
            "stream": False,
            "options": SCORING_PARAMS["ollama"]
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=TIMEOUTS["ollama"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}{OLLAMA_ENDPOINTS['generate']}",
                    json=payload
                ) as score_response:
                    return await self._process_scoring_response(score_response, response.model_name)
                    
        except Exception as e:
            return self.create_error_scoring(
                response.model_name,
                f"Ollama scoring failed: {str(e)}",
                0.3
            )
    
    async def _process_scoring_response(self, response: aiohttp.ClientResponse, target_model: str) -> ScoringResult:
        """Process the response from Ollama scoring API"""
        if response.status == 200:
            try:
                result = await response.json()
                evaluation = result.get("response", "")
                
                # Parse the evaluation
                overall_match = re.search(r'OVERALL:\s*([0-9.]+)', evaluation)
                reasoning_match = re.search(r'REASONING:\s*(.+)', evaluation, re.DOTALL)
                
                overall_score = float(overall_match.group(1)) if overall_match else 0.5
                reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
                
                return ScoringResult(
                    evaluator_model=f"{self.model_name} (Ollama)",
                    target_model=target_model,
                    score=max(0.0, min(1.0, overall_score)),
                    reasoning=reasoning,
                    criteria_scores={"overall": overall_score}
                )
                
            except Exception as parse_error:
                return self.create_error_scoring(
                    target_model,
                    f"Could not parse Ollama evaluation: {str(parse_error)}",
                    0.5
                )
        else:
            error_text = await response.text()
            return self.create_error_scoring(
                target_model,
                f"Ollama scoring error {response.status}: {error_text[:100]}",
                0.3
            )

async def get_ollama_models(base_url: str = DEFAULT_OLLAMA_URL) -> List[str]:
    """
    Fetch available models from Ollama
    
    Args:
        base_url: The base URL for the Ollama server
        
    Returns:
        List[str]: List of available model names
    """
    try:
        timeout = aiohttp.ClientTimeout(total=TIMEOUTS["ollama_models"])
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{base_url.rstrip('/')}{OLLAMA_ENDPOINTS['tags']}") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    return models
                else:
                    return []
    except Exception:
        return []