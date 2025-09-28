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
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
        }
        return {k: v for k, v in params.items() if v is not None}


class EvalType(Enum):
    CODE_SECURITY = "code_security"
    LOGS_ANALYZE = "logs_analyze"
    PHISHING_DETECTION = "phishing_detection"
    MALWARE_ANALYSIS = "malware_analysis"
    INTRUSION_DETECTION = "intrusion_detection"
    INCIDENT_RESPONSE = "incident_response"
    THREAT_INTELLIGENCE = "threat_intelligence"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    SQL_INJECTION = "sql_injection"
    XSS_DETECTION = "xss_detection"
    DDoS_DETECTION = "ddos_detection"
    RANSOMWARE_DETECTION = "ransomware_detection"
