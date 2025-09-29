from abc import ABC, abstractmethod

import kagglehub
import pandas as pd
from loguru import logger

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.schema import InputAnswerDict


class BaseDataLoader(ABC):
    def __init__(self, dataset_slug: str, file_path: str):
        self.dataset_slug = dataset_slug
        self.file_path = file_path

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def load(
        self,
        pandas_kwargs=None,
    ):
        logger.info(
            f"Loading Kaggle dataset: {self.dataset_slug}, "
            f"file: {self.file_path or '<root default>'}"
        )
        df = kagglehub.dataset_load(
            kagglehub.KaggleDatasetAdapter.PANDAS,
            self.dataset_slug,
            path=self.file_path,
            pandas_kwargs=pandas_kwargs or {},
        )
        logger.info(f"File: {self.file_path} initialized")
        return self._preprocess(df)

    @abstractmethod
    def _preprocess(self, df: pd.DataFrame) -> list[InputAnswerDict]:
        pass
