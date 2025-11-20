from dataclasses import dataclass
from enum import Enum


@dataclass
class ModelConfig:
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
        }
        return {k: v for k, v in params.items() if v is not None}


class EvalType(Enum):
    CODE_SECURITY = ("code_security", "binary")
    PHISHING_DETECTION = ("phishing_detection", "binary")
    VULNERABILITY_ASSESSMENT = ("vulnerability_assessment", "binary")
    MALWARE_ANALYSIS = ("malware_analysis", "binary")
    INTRUSION_DETECTION = ("intrusion_detection", "binary")
    INCIDENT_RESPONSE = ("incident_response", "binary")
    SQL_INJECTION = ("sql_injection", "binary")
    XSS_DETECTION = ("xss_detection", "binary")
    DDoS_DETECTION = ("ddos_detection", "binary")
    RANSOMWARE_DETECTION = ("ransomware_detection", "binary")
    CYBERSECURITY_MCQ = ("cybersecurity_mcq", "multiclass")

    def __init__(self, value, task_type):
        self._value_ = value
        self.task_type = task_type
