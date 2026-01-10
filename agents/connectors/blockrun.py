"""
BlockRun LLM Integration for Polymarket AI Agent.

This module provides a LangChain-compatible wrapper around blockrun-llm SDK,
enabling pay-per-request LLM access via x402 micropayments on Base.

Usage:
    from agents.connectors.blockrun import BlockRunLLM

    # Drop-in replacement for ChatOpenAI
    llm = BlockRunLLM(model="openai/gpt-4o-mini")
    result = llm.invoke([SystemMessage(...), HumanMessage(...)])
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class MockContent:
    """Mock response content for LangChain compatibility."""
    content: str


class BlockRunLLM:
    """
    LangChain-compatible LLM wrapper using BlockRun x402 payments.

    Drop-in replacement for ChatOpenAI that pays per request via Base USDC.
    """

    # Model mapping: langchain model names -> blockrun model names
    MODEL_MAP = {
        "gpt-4o": "openai/gpt-4o",
        "gpt-4o-mini": "openai/gpt-4o-mini",
        "gpt-4-1106-preview": "openai/gpt-4o",  # Map old model to new
        "gpt-3.5-turbo-16k": "openai/gpt-4o-mini",  # Map old model to new
        "claude-3-5-sonnet": "anthropic/claude-sonnet-4",
        "claude-3-5-haiku": "anthropic/claude-haiku-4.5",
    }

    def __init__(
        self,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0,
        max_tokens: int = 4096,
        private_key: Optional[str] = None,
    ):
        """
        Initialize BlockRun LLM client.

        Args:
            model: Model ID (e.g., "openai/gpt-4o-mini", "anthropic/claude-sonnet-4")
            temperature: Sampling temperature (default: 0)
            max_tokens: Max tokens to generate (default: 4096)
            private_key: Base wallet private key (or set BLOCKRUN_WALLET_KEY env)
        """
        # Normalize model name
        self.model = self.MODEL_MAP.get(model, model)
        self.model_name = self.model  # For compatibility with existing code
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Try to initialize blockrun-llm client
        self._client = None
        self._fallback_client = None

        try:
            from blockrun_llm import LLMClient
            key = private_key or os.getenv("BLOCKRUN_WALLET_KEY")
            if key:
                self._client = LLMClient(private_key=key)
                logger.info(f"BlockRun LLM initialized: {self.model}")
            else:
                logger.warning("BLOCKRUN_WALLET_KEY not set, using OpenAI fallback")
                self._init_fallback()
        except ImportError:
            logger.warning("blockrun-llm not installed, using OpenAI fallback")
            self._init_fallback()

    def _init_fallback(self):
        """Initialize OpenAI fallback client."""
        try:
            from langchain_openai import ChatOpenAI
            # Extract base model name for OpenAI
            base_model = self.model.replace("openai/", "")
            self._fallback_client = ChatOpenAI(
                model=base_model,
                temperature=self.temperature,
            )
            logger.info(f"Fallback to OpenAI: {base_model}")
        except Exception as e:
            logger.error(f"Failed to init OpenAI fallback: {e}")

    def _convert_messages(self, messages) -> List[Dict[str, str]]:
        """
        Convert LangChain messages to blockrun-llm format.

        LangChain: [SystemMessage(content="..."), HumanMessage(content="...")]
        BlockRun: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        result = []
        for msg in messages:
            # Determine role from message type
            role = "user"  # default

            if hasattr(msg, "__class__"):
                class_name = msg.__class__.__name__.lower()
                if "system" in class_name:
                    role = "system"
                elif "human" in class_name or "user" in class_name:
                    role = "user"
                elif "ai" in class_name or "assistant" in class_name:
                    role = "assistant"

            # Also check the type attribute (some LangChain messages use this)
            if hasattr(msg, "type"):
                msg_type = msg.type.lower()
                if msg_type == "human":
                    role = "user"
                elif msg_type == "ai":
                    role = "assistant"
                elif msg_type == "system":
                    role = "system"

            content = str(msg.content) if hasattr(msg, "content") else str(msg)
            result.append({"role": role, "content": content})

        return result

    def invoke(self, messages) -> MockContent:
        """
        Invoke the LLM with messages (LangChain-compatible interface).

        Args:
            messages: List of LangChain messages (SystemMessage, HumanMessage, etc.)

        Returns:
            Object with .content attribute containing response text
        """
        # Use BlockRun client if available
        if self._client:
            try:
                converted_messages = self._convert_messages(messages)
                result = self._client.chat_completion(
                    model=self.model,
                    messages=converted_messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature if self.temperature > 0 else None,
                )
                response_text = result.choices[0].message.content
                logger.debug(f"BlockRun response: {response_text[:100]}...")
                return MockContent(content=response_text)
            except Exception as e:
                logger.error(f"BlockRun error: {e}, falling back to OpenAI")
                if self._fallback_client:
                    return self._fallback_client.invoke(messages)
                raise

        # Use fallback client
        if self._fallback_client:
            return self._fallback_client.invoke(messages)

        raise RuntimeError("No LLM backend available. Install blockrun-llm or set OPENAI_API_KEY.")


def get_blockrun_llm(
    model: str = "openai/gpt-4o-mini",
    temperature: float = 0,
    **kwargs
) -> BlockRunLLM:
    """
    Factory function to create BlockRun LLM client.

    Args:
        model: Model ID (supports both "gpt-4o-mini" and "openai/gpt-4o-mini" formats)
        temperature: Sampling temperature
        **kwargs: Additional arguments passed to BlockRunLLM

    Returns:
        BlockRunLLM instance
    """
    return BlockRunLLM(model=model, temperature=temperature, **kwargs)
