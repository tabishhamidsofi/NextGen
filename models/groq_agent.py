# **Author**: Tabish Hamid
# **Date**: 2025-09-27
# **Description**: Groq model agent implementation.

import aiohttp
import asyncio
import re
from datetime import datetime
from typing import Dict, Any

from models.base import BaseModelAgent, ModelResponse, ScoringResult
from config.settings import (
    GROQ_BASE_URL, TIMEOUTS, GENERATION_PARAMS, 
    SCORING_PARAMS, SCORING_PROMPT_TEMPLATE
)

class GroqModelAgent(BaseModelAgent):
    """Agent for interacting with Groq API models"""
    
    def __init__(self, model_name: str, api_key: str):
        super().__init__(model_name)
        self.api_key = api_key
        self.base_url = GROQ_BASE_URL
    
    def _get_model_type(self) -> str:
        return "groq"
    
    async def generate_response(self, query: str) -> ModelResponse:
        """
        Generate a response from Groq model
        
        Args:
            query: The user's question
            
        Returns:
            ModelResponse: The model's response or error
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Provide comprehensive, accurate responses."
            },
            {
                "role": "user", 
                "content": query
            }
        ]
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            **GENERATION_PARAMS["groq"]
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=TIMEOUTS["groq"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    return await self._process_generation_response(response)
                    
        except asyncio.TimeoutError:
            return self.create_error_response("Request timed out", "Timeout error")
        except Exception as e:
            return self.create_error_response(f"Request failed: {str(e)}", "Request exception")
    
    async def _process_generation_response(self, response: aiohttp.ClientResponse) -> ModelResponse:
        """Process the response from Groq generation API"""
        if response.status == 200:
            try:
                response_data = await response.json()
                response_text = response_data["choices"][0]["message"]["content"]
                
                return ModelResponse(
                    model_name=f"{self.model_name} (Groq)",
                    response_text=response_text,
                    confidence=self._estimate_confidence(response_text),
                    reasoning="Groq API response",
                    timestamp=datetime.now()
                )
                
            except (KeyError, IndexError) as e:
                return self.create_error_response(
                    f"Unexpected API response format: {str(e)}", 
                    "API format error"
                )
        else:
            response_data = await response.text()
            return self.create_error_response(
                f"Groq API error {response.status}: {str(response_data)[:200]}", 
                "Failed request"
            )
    
    async def score_response(self, query: str, response: ModelResponse) -> ScoringResult:
        """
        Score a response using Groq model
        
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
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [{"role": "user", "content": scoring_prompt}]
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            **SCORING_PARAMS["groq"]
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=TIMEOUTS["groq"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as score_response:
                    return await self._process_scoring_response(score_response, response.model_name)
                    
        except Exception as e:
            return self.create_error_scoring(
                response.model_name,
                f"Scoring failed: {str(e)}",
                0.3
            )
    
    async def _process_scoring_response(self, response: aiohttp.ClientResponse, target_model: str) -> ScoringResult:
        """Process the response from Groq scoring API"""
        if response.status == 200:
            try:
                result = await response.json()
                evaluation = result["choices"][0]["message"]["content"]
                
                # Parse the evaluation
                overall_match = re.search(r'OVERALL:\s*([0-9.]+)', evaluation)
                reasoning_match = re.search(r'REASONING:\s*(.+)', evaluation, re.DOTALL)
                
                overall_score = float(overall_match.group(1)) if overall_match else 0.5
                reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
                
                return ScoringResult(
                    evaluator_model=f"{self.model_name} (Groq)",
                    target_model=target_model,
                    score=max(0.0, min(1.0, overall_score)),
                    reasoning=reasoning,
                    criteria_scores={"overall": overall_score}
                )
                
            except Exception as parse_error:
                return self.create_error_scoring(
                    target_model,
                    f"Could not parse evaluation: {str(parse_error)}",
                    0.5
                )
        else:
            error_text = await response.text()
            return self.create_error_scoring(
                target_model,
                f"Scoring API error {response.status}: {error_text[:100]}",
                0.3
            )