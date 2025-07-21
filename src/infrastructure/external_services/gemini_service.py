from google import genai
import os 
import logging
from typing import Optional,Dict,Any,List
import asyncio
from datetime import datetime
from infrastructure.config.app_config import config
import json

import random
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key=config.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.client=genai.Client(api_key=self.api_key)
        self.model_name=config.gemini_model
        if not self.model_name:
            raise ValueError("GEMINI_MODEL environment variable is not set")
        
        self.is_connected = False
    
    async def connect(self):
        try:
            await self.health_check()
            self.is_connected = True
            logger.info("Gemini Service conectado exitosamente")
        except Exception as e:
            logger.error(f"Error conectando a Gemini Service: {e}")
            raise

    async def health_check(self)->bool:
        try:
            response=await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents="Test connection",
            )
            return response.text is not None
        except Exception as e:
            logger.info(f"Health check failed: {e}")
            return False
    
    async def generate_content(self, prompt: str, max_tokens: int = 100) -> Optional[str]:
        if not self.is_connected:
            await self.connect()
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                max_output_tokens=max_tokens
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return None
        
    async def generate_quiz(self, skill: str):
        if not self.is_connected:
            await self.connect()
        try:
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=f"""
Generate 15 questions to assess general knowledge of the skill: {skill}.

Each question must include a "subcategory" related to the core topics within {skill}. For example, if the skill is "UX/UI Design", subcategories may include:
- Understanding UX Principles
- User Research
- Wireframing and Prototyping
- UI Design Patterns
- Usability Testing
- Accessibility
- Design Systems
(You may define appropriate subcategories for other skills.)

All questions must be multiple choice. Do not use other types such as true/false, open, or analysis.

Return a JSON object in the following structure:

""" + """{
  
  "questions": [
    {
      "id":number,
      "subcategory": "Subcategory name",
      "type": "multiple",
      "question": "Text",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "Correct option letter or text",
      "recommended_tools": ["Tool1", "Tool2"]
    }
  ]
}

Only return a valid JSON. Do not include any explanation or text outside the JSON.
"""
            )
            
            
            if response and response.text:
                try:
                    # Limpiar el texto JSON
                    json_text = response.text.strip()
                    
                   
                    if json_text.startswith('```json'):
                        json_text = json_text[7:-3]  
                    elif json_text.startswith('```'):
                        json_text = json_text[3:-3]  
                    
                
                    quiz_data = json.loads(json_text)
                    logger.info(f"Quiz generado exitosamente para skill: {skill}")
                    return quiz_data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON response: {e}")
                    logger.error(f"Response text: {response.text}")
                    return None
            
            logger.warning(f"No se pudo generar quiz para skill: {skill}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating quiz for skill {skill}: {e}")
            return None
    async def generate_quiz_with_retry(self, skill: str, max_retries: int = 3) -> Optional[Dict]:
        """Generar quiz con reintentos automáticos"""
        for attempt in range(max_retries + 1):
            try:
                return await self.generate_quiz(skill)
                
            except Exception as e:
                error_message = str(e).lower()
                
                # Verificar si es error 503 o sobrecarga
                if "503" in error_message or "overloaded" in error_message or "unavailable" in error_message:
                    if attempt < max_retries:
                        # Exponential backoff: 2^attempt + random jitter
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Gemini overloaded. Retry {attempt + 1}/{max_retries} in {wait_time:.2f}s")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Gemini still overloaded after {max_retries} retries")
                        return None
                else:
                    # Error diferente, no reintentar
                    logger.error(f"Non-retryable error: {e}")
                    raise e
        
        return None