"""
Multi-Modal Agent Support
Process text + images + voice simultaneously for comprehensive understanding
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import base64
import io

logger = logging.getLogger(__name__)

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available, image processing disabled")
    PIL_AVAILABLE = False


class ModalityType(str, Enum):
    """Types of input modalities"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass
class MultiModalInput:
    """Multi-modal input container"""
    text: Optional[str] = None
    images: Optional[List[bytes]] = None
    audio: Optional[bytes] = None
    video: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MultiModalOutput:
    """Multi-modal processing output"""
    text_response: str
    vision_analysis: Optional[Dict[str, Any]] = None
    audio_transcript: Optional[str] = None
    audio_response: Optional[bytes] = None
    reasoning: Optional[str] = None
    actions: Optional[List[Dict[str, Any]]] = None
    confidence: float = 0.0
    processing_time_ms: int = 0


class MultiModalAgent:
    """
    Multi-modal agent processor
    Handles text, images, and voice inputs simultaneously
    """
    
    def __init__(
        self,
        text_model: str = "claude-3-5-sonnet-20241022",
        vision_model: str = "claude-3-5-haiku-20241022",
        audio_model: str = "whisper-1"
    ):
        self.text_model = text_model
        self.vision_model = vision_model
        self.audio_model = audio_model
        
        self.max_image_size = 20 * 1024 * 1024  # 20MB
        self.max_audio_duration = 300  # 5 minutes
        
        # Initialize clients (lazy loading)
        self._text_client = None
        self._vision_client = None
        self._audio_client = None
    
    async def process_multimodal_task(
        self,
        inputs: MultiModalInput
    ) -> MultiModalOutput:
        """
        Process multi-modal inputs and generate comprehensive response
        
        Args:
            inputs: MultiModalInput containing text, images, audio, etc.
        
        Returns:
            MultiModalOutput with analysis, reasoning, and actions
        """
        import time
        start_time = time.time()
        
        # Process each modality in parallel
        tasks = []
        
        if inputs.text:
            tasks.append(self._process_text(inputs.text))
        
        if inputs.images:
            tasks.append(self._process_images(inputs.images))
        
        if inputs.audio:
            tasks.append(self._process_audio(inputs.audio))
        
        # Execute all modality processors in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Extract results
        text_result = None
        vision_result = None
        audio_result = None
        
        result_idx = 0
        if inputs.text:
            text_result = results[result_idx] if not isinstance(results[result_idx], Exception) else None
            result_idx += 1
        
        if inputs.images:
            vision_result = results[result_idx] if not isinstance(results[result_idx], Exception) else None
            result_idx += 1
        
        if inputs.audio:
            audio_result = results[result_idx] if not isinstance(results[result_idx], Exception) else None
            result_idx += 1
        
        # Synthesize multi-modal understanding
        synthesis = await self._synthesize_multimodal(
            text_result=text_result,
            vision_result=vision_result,
            audio_result=audio_result,
            original_inputs=inputs
        )
        
        # Generate actions based on synthesis
        actions = await self._generate_actions(synthesis)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return MultiModalOutput(
            text_response=synthesis.get("response", ""),
            vision_analysis=vision_result,
            audio_transcript=audio_result.get("transcript") if audio_result else None,
            audio_response=None,  # TODO: TTS integration
            reasoning=synthesis.get("reasoning", ""),
            actions=actions,
            confidence=synthesis.get("confidence", 0.0),
            processing_time_ms=processing_time
        )
    
    async def _process_text(self, text: str) -> Dict[str, Any]:
        """Process text input"""
        try:
            # Use LLM for text understanding
            from langchain_anthropic import ChatAnthropic
            
            llm = ChatAnthropic(model=self.text_model, temperature=0.7)
            
            prompt = f"""Analyze the following text and extract:
1. Main intent
2. Key entities
3. Sentiment
4. Required actions

Text: {text}

Provide structured analysis."""
            
            response = await llm.ainvoke(prompt)
            
            return {
                "raw_text": text,
                "analysis": response.content,
                "model": self.text_model
            }
        
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return {
                "raw_text": text,
                "analysis": text,
                "error": str(e)
            }
    
    async def _process_images(self, images: List[bytes]) -> Dict[str, Any]:
        """Process image inputs"""
        try:
            if not PIL_AVAILABLE:
                return {"error": "Image processing not available"}
            
            analyses = []
            
            for idx, image_bytes in enumerate(images):
                # Validate image size
                if len(image_bytes) > self.max_image_size:
                    logger.warning(f"Image {idx} exceeds max size, skipping")
                    continue
                
                # Analyze image
                analysis = await self._analyze_single_image(image_bytes)
                analyses.append(analysis)
            
            return {
                "image_count": len(images),
                "analyses": analyses,
                "model": self.vision_model
            }
        
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_single_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze a single image using vision model"""
        try:
            # Convert to base64 for API
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Use vision-capable LLM
            from langchain_anthropic import ChatAnthropic
            from langchain_core.messages import HumanMessage
            
            llm = ChatAnthropic(model=self.vision_model, temperature=0)
            
            message = HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this image and provide:
1. Main objects/subjects
2. Scene description
3. Text content (if any)
4. Relevant context
5. Potential actions or insights"""
                    }
                ]
            )
            
            response = await llm.ainvoke([message])
            
            return {
                "description": response.content,
                "confidence": 0.85
            }
        
        except Exception as e:
            logger.error(f"Single image analysis failed: {e}")
            return {
                "description": "Image analysis unavailable",
                "error": str(e)
            }
    
    async def _process_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Process audio input (speech-to-text)"""
        try:
            # Use Whisper or similar for transcription
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI()
            
            # Convert bytes to file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.mp3"
            
            # Transcribe
            transcript = await client.audio.transcriptions.create(
                model=self.audio_model,
                file=audio_file,
                response_format="verbose_json"
            )
            
            return {
                "transcript": transcript.text,
                "language": transcript.language if hasattr(transcript, 'language') else "en",
                "duration": transcript.duration if hasattr(transcript, 'duration') else 0,
                "confidence": 0.9
            }
        
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return {
                "transcript": "",
                "error": str(e)
            }
    
    async def _synthesize_multimodal(
        self,
        text_result: Optional[Dict[str, Any]],
        vision_result: Optional[Dict[str, Any]],
        audio_result: Optional[Dict[str, Any]],
        original_inputs: MultiModalInput
    ) -> Dict[str, Any]:
        """
        Synthesize understanding from multiple modalities
        """
        try:
            # Combine all modality results
            combined_context = []
            
            if text_result:
                combined_context.append(f"Text Analysis:\n{text_result.get('analysis', '')}")
            
            if vision_result and vision_result.get('analyses'):
                vision_desc = "\n".join([
                    f"Image {i+1}: {analysis.get('description', '')}"
                    for i, analysis in enumerate(vision_result['analyses'])
                ])
                combined_context.append(f"Vision Analysis:\n{vision_desc}")
            
            if audio_result and audio_result.get('transcript'):
                combined_context.append(f"Audio Transcript:\n{audio_result['transcript']}")
            
            full_context = "\n\n".join(combined_context)
            
            # Use LLM to synthesize comprehensive understanding
            from langchain_anthropic import ChatAnthropic
            
            llm = ChatAnthropic(model=self.text_model, temperature=0.7)
            
            synthesis_prompt = f"""You are analyzing multi-modal input. Synthesize the following information into a comprehensive understanding:

{full_context}

Provide:
1. Unified understanding of the situation
2. Key insights from combining modalities
3. Recommended response or actions
4. Confidence level (0-1)

Format as JSON with keys: understanding, insights, response, confidence"""
            
            response = await llm.ainvoke(synthesis_prompt)
            
            # Parse response (simplified - would use structured output in production)
            import json
            try:
                synthesis = json.loads(response.content)
            except:
                synthesis = {
                    "understanding": response.content,
                    "response": response.content,
                    "confidence": 0.7
                }
            
            return {
                "response": synthesis.get("response", ""),
                "reasoning": synthesis.get("understanding", ""),
                "insights": synthesis.get("insights", []),
                "confidence": synthesis.get("confidence", 0.7)
            }
        
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {
                "response": "Unable to synthesize multi-modal understanding",
                "error": str(e),
                "confidence": 0.0
            }
    
    async def _generate_actions(self, synthesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable items from synthesis"""
        try:
            # Extract actions from synthesis
            response = synthesis.get("response", "")
            
            # Simple action extraction (would be more sophisticated in production)
            actions = []
            
            # Look for action keywords
            action_keywords = ["should", "must", "need to", "recommend", "suggest"]
            
            for line in response.split("\n"):
                if any(keyword in line.lower() for keyword in action_keywords):
                    actions.append({
                        "type": "recommendation",
                        "description": line.strip(),
                        "priority": "medium"
                    })
            
            return actions if actions else [{
                "type": "response",
                "description": "Provide information to user",
                "priority": "low"
            }]
        
        except Exception as e:
            logger.error(f"Action generation failed: {e}")
            return []


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_multimodal():
        agent = MultiModalAgent()
        
        # Test with text only
        inputs = MultiModalInput(
            text="Analyze this customer support ticket: Customer reports app crashing on iOS 17"
        )
        
        result = await agent.process_multimodal_task(inputs)
        
        print(f"Response: {result.text_response}")
        print(f"Reasoning: {result.reasoning}")
        print(f"Actions: {result.actions}")
        print(f"Confidence: {result.confidence}")
        print(f"Processing time: {result.processing_time_ms}ms")
    
    asyncio.run(test_multimodal())

