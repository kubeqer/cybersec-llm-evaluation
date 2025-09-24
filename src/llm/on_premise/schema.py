from dataclasses import dataclass
from enum import Enum
from typing import Literal


class EvalType(Enum):
    CODE_SECURITY = "code_security"
    LOGS_ANALYZE = "logs_analyze"


@dataclass
class ModelConfig:
    model_name: str
    provider: Literal[
        "black-forest-labs",
        "cerebras",
        "cohere",
        "fal-ai",
        "featherless-ai",
        "fireworks-ai",
        "groq",
        "hf-inference",
        "hyperbolic",
        "nebius",
        "novita",
        "nscale",
        "openai",
        "publicai",
        "replicate",
        "sambanova",
        "scaleway",
        "together",
        "auto",
    ] = "auto"
    max_tokens: int = 2048
    temperature: float = 0.0
    top_p: float = 0.95
    top_k: int = 50
    repetition_penalty: float = 1.0
    timeout: int = 120

    def to_generation_params(self) -> dict[str, object]:
        params = {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
        }
        return {k: v for k, v in params.items() if v is not None}
