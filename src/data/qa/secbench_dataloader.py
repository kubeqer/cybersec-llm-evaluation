import pandas as pd
from datasets import load_dataset  # type: ignore[import-untyped]

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.qa.utils import format_options
from src.data.schema import InputAnswerDict


class SecBenchDataLoader:
    """
    DataLoader for SecBench: A Comprehensive Multi-Dimensional Benchmarking Dataset
    for LLMs in Cybersecurity.
    SecBench is a multi-dimensional dataset with:
    - Multi-Level: Knowledge Retention (KR) and Logical Reasoning (LR)
    - Multi-Domain: 9 security domains (D1-D9)
    - Multi-Form: MCQs (Multiple Choice Questions) and SAQs (Short Answer Questions)
    - Multi-Language: Chinese and English
    Domains:
        D1. Security Management
        D2. Data Security
        D3. Network and Infrastructure Security
        D4. Security Standards and Regulations
        D5. Application Security
        D6. Identity and Access Control
        D7. Fundamental Software and Hardware Technology
        D8. Endpoint and Host Security
        D9. Cloud Security
    Source: https://huggingface.co/datasets/secbench-hf/SecBench
    """

    DATASET_SLUG = "secbench-hf/SecBench"
    DEFAULT_SPLIT = "test"

    DOMAIN_MAPPING = {
        "D1": "Security Management",
        "D2": "Data Security",
        "D3": "Network and Infrastructure Security",
        "D4": "Security Standards and Regulations",
        "D5": "Application Security",
        "D6": "Identity and Access Control",
        "D7": "Fundamental Software and Hardware Technology",
        "D8": "Endpoint and Host Security",
        "D9": "Cloud Security",
    }

    def __init__(
        self,
        split: str = "test",
        question_type: str | None = None,
        level: str | None = None,
        language: str | None = None,
        domain: str | None = None,
    ):
        """
        Initialize the SecBench dataloader.
        Args:
            split: Dataset split to load. Default is 'test'.
            question_type: Filter by question type ('MCQ' or 'SAQ'). None for all.
            level: Filter by capability level ('KR' or 'LR'). None for all.
            language: Filter by language ('English' or 'Chinese'). None for all.
            domain: Filter by domain ('D1' through 'D9'). None for all.
        """
        self.split = split
        self.question_type = question_type
        self.level = level
        self.language = language
        self.domain = domain

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def load(self) -> list[InputAnswerDict]:
        """Load and preprocess the SecBench dataset."""
        dataset = load_dataset(self.DATASET_SLUG, split=self.split)
        df = pd.DataFrame(dataset)
        result: list[InputAnswerDict] = self._preprocess(df)
        return result

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def _preprocess(self, df: pd.DataFrame) -> list[InputAnswerDict]:
        """
        Preprocess the dataset into InputAnswerDict format.
        Applies filters based on initialization parameters and formats
        questions appropriately for MCQs and SAQs.
        """
        df = df.fillna("")

        # Apply filters
        if self.question_type:
            if "type" in df.columns:
                df = df[df["type"] == self.question_type]
            elif "question_type" in df.columns:
                df = df[df["question_type"] == self.question_type]

        if self.level:
            if "level" in df.columns:
                df = df[df["level"] == self.level]
            elif "ability" in df.columns:
                df = df[df["ability"] == self.level]

        if self.language and "language" in df.columns:
            df = df[df["language"] == self.language]

        if self.domain and "domain" in df.columns:
            df = df[df["domain"] == self.domain]

        # Format input based on question structure
        df["Input"] = df.apply(self._format_question, axis=1)
        df["Answer"] = df.apply(self._extract_answer, axis=1)

        result: list[InputAnswerDict] = [
            InputAnswerDict(input=str(row.Input), answer=str(row.Answer))
            for row in df[["Input", "Answer"]].itertuples(index=False)
        ]
        return result

    def _format_question(self, row: pd.Series) -> str:
        question = row.get("question", "")
        metadata_parts = []
        if row["domain"]:
            domain_name = self.DOMAIN_MAPPING.get(row["domain"], row["domain"])
            metadata_parts.append(f"Domain: {domain_name}")
        if row["level"]:
            level_name = (
                "Knowledge Retention" if row["level"] == "KR" else "Logical Reasoning"
            )
            metadata_parts.append(f"Level: {level_name}")
        parts = []
        if metadata_parts:
            parts.append(f"[{' | '.join(metadata_parts)}]")

        parts.append(f"Question: {question}")

        # Add options for MCQs
        if row["options"]:
            options_str = format_options(row["options"])
            if options_str:
                parts.append(f"\nOptions:\n{options_str}")
        elif row["choices"]:
            options_str = format_options(row["choices"])
            if options_str:
                parts.append(f"\nOptions:\n{options_str}")

        return "\n".join(parts)

    @staticmethod
    def _extract_answer(row: pd.Series) -> str:
        """Extract the answer from the row."""
        for field in ["answer", "correct_answer", "gold_answer", "label"]:
            if row[field]:
                return str(row[field])
        return ""
