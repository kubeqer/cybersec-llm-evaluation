from huggingface_hub import InferenceClient

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.core.settings.settings import settings
from src.llm.on_premise.schema import EvalType, ModelConfig


class BaseHF:
    def __init__(
        self,
        model_config: ModelConfig,
        auto_save: bool = True,
    ):
        self.model_config: ModelConfig = model_config
        self.auto_save: bool = auto_save
        self.system_prompt: dict[str, str] = {
            EvalType.CODE_SECURITY.value: """You are a code security expert.
Analyze the provided code for potential security vulnerabilities, including but not limited to:
- SQL injection
- XSS vulnerabilities
- Authentication bypasses
- Data leakage risks
- Input validation issues
Provide specific recommendations for fixes.""",  # noqa: E501
            EvalType.LOGS_ANALYZE.value: """You are a log analysis expert.
Analyze the provided logs to identify:
- Error patterns
- Security incidents
- Anomalous behavior
Provide actionable insights and recommendations.""",  # noqa: E501
        }
        self.client = InferenceClient(
            provider=self.model_config.provider,
            timeout=self.model_config.timeout,
            token=settings.hf_token,
        )

    @error_handling
    @log_calls
    def generate(self, message: str, eval_type: EvalType) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_config.model_name,
            messages=[
                {
                    "role": "assistant",
                    "content": self.system_prompt.get(eval_type.value),
                },
                {"role": "user", "content": message},
            ],
            **self.model_config.to_generation_params(),
        )
        return str(completion.choices[0].message)
