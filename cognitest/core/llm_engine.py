"""
CogniTest Framework - LLM Engine
Author: Çağrı Temel
Description: Core LLM integration using Mistral-7B-Instruct
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM model"""
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    temperature: float = 0.3
    top_p: float = 0.85
    max_tokens: int = 2048
    repetition_penalty: float = 1.15
    load_in_4bit: bool = True


class LLMEngine:
    """
    Core LLM engine for CogniTest framework.
    Handles model loading, inference, and prompt management.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM engine with Mistral-7B-Instruct.

        Args:
            config: LLM configuration parameters
        """
        self.config = config or LLMConfig()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None

        logger.info(f"Initializing LLM Engine on device: {self.device}")
        self._load_model()

    def _load_model(self):
        """Load Mistral model with 4-bit quantization for efficiency"""
        try:
            logger.info(f"Loading model: {self.config.model_name}")

            # Configure 4-bit quantization for memory efficiency
            if self.config.load_in_4bit and self.device == "cuda":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True
                )

                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None,
                    trust_remote_code=True
                )

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                trust_remote_code=True
            )

            # Set padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from prompt using Mistral model.

        Args:
            prompt: Input prompt text
            **kwargs: Override default generation parameters

        Returns:
            Generated text response
        """
        try:
            # Format prompt for Mistral instruction format
            formatted_prompt = f"[INST] {prompt} [/INST]"

            # Tokenize input
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=4096
            ).to(self.device)

            # Generation parameters
            gen_params = {
                "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "repetition_penalty": kwargs.get("repetition_penalty", self.config.repetition_penalty),
                "do_sample": True,
                "pad_token_id": self.tokenizer.pad_token_id,
                "eos_token_id": self.tokenizer.eos_token_id
            }

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **gen_params)

            # Decode and extract response
            full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the response part (after [/INST])
            if "[/INST]" in full_text:
                response = full_text.split("[/INST]")[-1].strip()
            else:
                response = full_text.strip()

            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def generate_batch(self, prompts: List[str], **kwargs) -> List[str]:
        """
        Generate responses for multiple prompts in batch.

        Args:
            prompts: List of input prompts
            **kwargs: Override default generation parameters

        Returns:
            List of generated responses
        """
        responses = []
        for prompt in prompts:
            response = self.generate(prompt, **kwargs)
            responses.append(response)
        return responses

    def get_model_info(self) -> Dict[str, any]:
        """Get information about loaded model"""
        return {
            "model_name": self.config.model_name,
            "device": self.device,
            "parameters": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "max_tokens": self.config.max_tokens,
                "repetition_penalty": self.config.repetition_penalty
            },
            "quantization": "4-bit" if self.config.load_in_4bit else "float16/32"
        }


if __name__ == "__main__":
    # Test LLM Engine
    engine = LLMEngine()
    print(engine.get_model_info())

    test_prompt = "Explain what a pytest fixture is in 2 sentences."
    response = engine.generate(test_prompt)
    print(f"\nPrompt: {test_prompt}")
    print(f"Response: {response}")