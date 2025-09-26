"""Importance scoring for memories using LLM."""

import json
import logging
import re
from typing import Optional

from ..config import Settings
from ..models.memory import Memory, MemoryType
from .ollama_client import OllamaClient, OllamaError

logger = logging.getLogger(__name__)


class ImportanceScorer:
    """Service for scoring memory importance using LLM."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize importance scorer.
        
        Args:
            settings: Application settings (will use defaults if None)
        """
        if settings is None:
            from ..config import get_settings
            settings = get_settings()
        
        self.settings = settings
        self.ollama_client = OllamaClient(
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout
        )
    
    def _build_importance_prompt(self, memory: Memory, agent_context: str = "") -> str:
        """Build prompt for importance scoring.
        
        Args:
            memory: Memory to score
            agent_context: Additional context about the agent
            
        Returns:
            Formatted prompt for LLM
        """
        memory_type_descriptions = {
            MemoryType.PERCEPTION: "something the agent observed",
            MemoryType.ACTION: "something the agent did", 
            MemoryType.DIALOGUE: "a conversation the agent had",
            MemoryType.REFLECTION: "an insight the agent had",
            MemoryType.PLAN: "planning-related information"
        }
        
        memory_desc = memory_type_descriptions.get(memory.memory_type, "a memory")
        
        prompt = f"""Rate the importance of this memory for an agent on a scale of 1-10, where:
1 = Completely mundane and unimportant (e.g., "I walked down the street")
5 = Moderately important (e.g., "I had coffee with a friend")
10 = Extremely significant and life-changing (e.g., "I got married", "Someone close to me died")

Memory type: {memory_desc}
Memory content: "{memory.content}"
Location: {memory.location or "unknown"}

{f"Agent context: {agent_context}" if agent_context else ""}

Consider:
- How emotionally significant is this memory?
- How much will this affect the agent's future behavior?
- How memorable would this be to a real person?
- Does this involve major life events, relationships, or personal growth?

Respond with only a number from 1-10, no explanation needed."""

        return prompt
    
    async def score_importance(
        self, 
        memory: Memory, 
        agent_context: str = ""
    ) -> float:
        """Score the importance of a memory.
        
        Args:
            memory: Memory to score
            agent_context: Additional context about the agent
            
        Returns:
            Importance score from 0.0 to 10.0
            
        Raises:
            OllamaError: If scoring fails
        """
        # Some heuristic rules for basic scoring
        base_score = self._get_heuristic_score(memory)
        
        try:
            # Get LLM scoring
            llm_score = await self._get_llm_score(memory, agent_context)
            
            # Combine heuristic and LLM scores (weighted average)
            final_score = (base_score * 0.3) + (llm_score * 0.7)
            
            # Clamp to valid range
            final_score = max(0.0, min(10.0, final_score))
            
            logger.debug(
                f"Scored memory importance: heuristic={base_score:.1f}, "
                f"llm={llm_score:.1f}, final={final_score:.1f}"
            )
            
            return final_score
            
        except Exception as e:
            logger.warning(f"LLM scoring failed, using heuristic only: {e}")
            return base_score
    
    def _get_heuristic_score(self, memory: Memory) -> float:
        """Get heuristic importance score based on rules.
        
        Args:
            memory: Memory to score
            
        Returns:
            Heuristic importance score
        """
        content_lower = memory.content.lower()
        score = 3.0  # Base score
        
        # Memory type adjustments
        if memory.memory_type == MemoryType.REFLECTION:
            score += 2.0  # Reflections are inherently important
        elif memory.memory_type == MemoryType.DIALOGUE:
            score += 1.0  # Conversations are moderately important
        elif memory.memory_type == MemoryType.ACTION:
            score += 0.5  # Actions are slightly more important than perceptions
        
        # Content-based adjustments
        high_importance_keywords = [
            "death", "died", "funeral", "birth", "born", "marriage", "married",
            "love", "hate", "angry", "furious", "ecstatic", "devastated",
            "accident", "emergency", "crisis", "celebration", "party",
            "promotion", "fired", "hired", "graduated", "failed"
        ]
        
        moderate_importance_keywords = [
            "friend", "family", "relationship", "meeting", "important",
            "decision", "plan", "goal", "achievement", "problem", "issue"
        ]
        
        for keyword in high_importance_keywords:
            if keyword in content_lower:
                score += 2.0
                break
        
        for keyword in moderate_importance_keywords:
            if keyword in content_lower:
                score += 1.0
                break
        
        # Emotional indicators
        if any(emotion in content_lower for emotion in ["happy", "sad", "excited", "worried", "surprised"]):
            score += 0.5
        
        # Question marks might indicate uncertainty or curiosity
        if "?" in memory.content:
            score += 0.3
        
        # Exclamation marks indicate strong emotion
        if "!" in memory.content:
            score += 0.5
        
        return min(10.0, max(1.0, score))
    
    async def _get_llm_score(self, memory: Memory, agent_context: str) -> float:
        """Get LLM-based importance score.
        
        Args:
            memory: Memory to score
            agent_context: Agent context
            
        Returns:
            LLM importance score
            
        Raises:
            OllamaError: If LLM scoring fails
        """
        prompt = self._build_importance_prompt(memory, agent_context)
        
        async with self.ollama_client as client:
            response = await client.generate(
                model=self.settings.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.1,  # Low temperature for consistent scoring
                    "top_p": 0.9,
                    "num_predict": 10   # Short response expected
                }
            )
            
            # Extract numeric score from response
            score_text = response.response.strip()
            
            # Try to extract a number from the response
            numbers = re.findall(r'\d+(?:\.\d+)?', score_text)
            if numbers:
                score = float(numbers[0])
                # Ensure score is in valid range
                if 1.0 <= score <= 10.0:
                    return score
            
            # If parsing fails, log and fall back
            logger.warning(f"Could not parse LLM importance score: '{score_text}'")
            raise OllamaError(f"Invalid LLM response for importance scoring: {score_text}")
    
    async def health_check(self) -> bool:
        """Check if the importance scorer is working.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with self.ollama_client as client:
                health = await client.health_check()
                if not health:
                    return False
                
                # Test importance scoring
                test_memory = Memory(
                    agent_id="test",
                    content="This is a test memory for health checking",
                    memory_type=MemoryType.PERCEPTION
                )
                
                score = await self.score_importance(test_memory)
                return 0.0 <= score <= 10.0
                
        except Exception as e:
            logger.warning(f"Importance scorer health check failed: {e}")
            return False
