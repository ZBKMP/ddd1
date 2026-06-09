# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Storage functions for the GraphRAG run module."""

import logging
from io import BytesIO
from pathlib import Path

import pandas as pd

from graphrag.storage.pipeline_storage import PipelineStorage

logger = logging.getLogger(__name__)

_DEBUG_LOG_PATH = Path(__file__).resolve().parents[2] / "debug-d938bd.log"


def _agent_debug_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    import json
    import time

    entry = {
        "sessionId": "d938bd",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    with _DEBUG_LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry) + "\n")
    # #endregion


def _coerce_string_column(series: pd.Series) -> pd.Series:
    return series.map(lambda value: None if pd.isna(value) else str(value))


def _prepare_dataframe_for_parquet(table: pd.DataFrame) -> pd.DataFrame:
    """Coerce mixed-type columns so parquet export succeeds."""
    prepared = table.copy()
    for column in ("id", "text"):
        if column in prepared.columns:
            prepared[column] = _coerce_string_column(prepared[column])
    return prepared


async def load_table_from_storage(name: str, storage: PipelineStorage) -> pd.DataFrame:
    """Load a parquet from the storage instance."""
    filename = f"{name}.parquet"
    if not await storage.has(filename):
        msg = f"Could not find {filename} in storage!"
        raise ValueError(msg)
    try:
        logger.info("reading table from storage: %s", filename)
        return pd.read_parquet(BytesIO(await storage.get(filename, as_bytes=True)))
    except Exception:
        logger.exception("error loading table from storage: %s", filename)
        raise


async def write_table_to_storage(
    table: pd.DataFrame, name: str, storage: PipelineStorage
) -> None:
    """Write a table to storage."""
    if "id" in table.columns or "text" in table.columns:
        debug_data: dict[str, object] = {"table": name}
        if "id" in table.columns:
            id_sample = table["id"].head(5).tolist()
            debug_data["id_dtype"] = str(table["id"].dtype)
            debug_data["id_types"] = sorted(
                {type(v).__name__ for v in table["id"].head(100).tolist()}
            )
            debug_data["id_sample"] = [str(v) for v in id_sample]
        if "text" in table.columns:
            text_sample = table["text"].head(5).tolist()
            debug_data["text_dtype"] = str(table["text"].dtype)
            debug_data["text_types"] = sorted(
                {type(v).__name__ for v in table["text"].head(100).tolist()}
            )
            debug_data["text_sample"] = [str(v)[:80] for v in text_sample]
        # #region agent log
        _agent_debug_log(
            "H",
            "storage.py:write_table_to_storage",
            "columns before parquet",
            debug_data,
        )
        # #endregion
    prepared = _prepare_dataframe_for_parquet(table)
    await storage.set(f"{name}.parquet", prepared.to_parquet())


async def delete_table_from_storage(name: str, storage: PipelineStorage) -> None:
    """Delete a table to storage."""
    await storage.delete(f"{name}.parquet")


async def storage_has_table(name: str, storage: PipelineStorage) -> bool:
    """Check if a table exists in storage."""
    return await storage.has(f"{name}.parquet")
