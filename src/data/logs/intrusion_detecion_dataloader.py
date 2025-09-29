from typing import cast

import pandas as pd
from loguru import logger

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.base import BaseDataLoader
from src.data.schema import InputAnswerDict


class IntrusionDetectionDataLoader(BaseDataLoader):
    DATASET_SLUG = "developerghost/intrusion-detection-logs-normal-bot-scan"
    FILE_PATH = "Network_logs.csv"
    FEATURE_COLUMNS = [
        "Source_IP",
        "Destination_IP",
        "Port",
        "Request_Type",
        "Protocol",
        "Payload_Size",
        "User_Agent",
        "Status",
        "Scan_Type",
    ]
    INPUT_TEMPLATE = (
        "Source_IP: {Source_IP}, "
        "Destination_IP: {Destination_IP}, "
        "Port: {Port}, "
        "Request_Type: {Request_Type}, "
        "Protocol: {Protocol}, "
        "Payload_Size: {Payload_Size}, "
        "User_Agent: {User_Agent}, "
        "Status: {Status}, "
        "Scan_Type: {Scan_Type}"
    )

    def __init__(self):
        super().__init__(dataset_slug=self.DATASET_SLUG, file_path=self.FILE_PATH)

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def _preprocess(self, df: pd.DataFrame) -> list[InputAnswerDict]:
        if not all(col in df.columns for col in self.FEATURE_COLUMNS):
            missing = [col for col in self.FEATURE_COLUMNS if col not in df.columns]
            logger.error(f"DataFrame is missing required feature columns: {missing}")
            raise ValueError("Required feature columns are missing.")
        if "Intrusion" in df.columns:
            try:
                df["Intrusion"] = df["Intrusion"].astype(int)
                logger.info("Normalized 'Intrusion' column to integer type.")
            except ValueError:
                logger.error(
                    "Could not convert 'Intrusion' column to integer. "
                    "Check data values."
                )
        else:
            logger.warning("'Intrusion' target column not found.")
        df["Input"] = df.apply(lambda row: self.INPUT_TEMPLATE.format(**row), axis=1)
        return [
            InputAnswerDict(input=str(row.Input), answer=int(cast(int, row.Intrusion)))
            for row in df[["Input", "Intrusion"]].itertuples(index=False)
        ]
