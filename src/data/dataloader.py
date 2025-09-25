import kagglehub
from loguru import logger

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls


class DataLoader:
    def __init__(self, dataset_slug: str):
        self.dataset_slug = dataset_slug

    @error_handling
    @log_calls
    def load(self, file_path: str | None = None, pandas_kwargs=None, sql_query=None):
        logger.info(
            f"Loading Kaggle dataset: {self.dataset_slug}, "
            f"file: {file_path or '<root default>'}"
        )
        load_kwargs = {
            "adapter": kagglehub.KaggleDatasetAdapter.PANDAS,
            "dataset": self.dataset_slug,
            "sql_query": sql_query,
            "pandas_kwargs": pandas_kwargs or {},
        }
        if file_path is not None:
            load_kwargs["path"] = file_path
        df = kagglehub.dataset_load(**load_kwargs)
        return df

    @staticmethod
    def normalize(df):
        return df.to_dict(orient="records")
