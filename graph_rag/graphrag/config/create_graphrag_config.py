# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Parameterization settings for the default configuration, loaded from environment variables."""

from copy import deepcopy
from pathlib import Path
from typing import Any

import graphrag.config.defaults as defs
from graphrag.config.enums import ModelType
from graphrag.config.models.graph_rag_config import GraphRagConfig

_WORKFLOW_MODEL_ID_SECTIONS = (
    "extract_graph",
    "summarize_descriptions",
    "extract_claims",
    "community_reports",
)
_SEARCH_CHAT_MODEL_SECTIONS = (
    "local_search",
    "global_search",
    "drift_search",
    "basic_search",
)


def _normalize_language_model_entry(
    model_id: str, entry: dict[str, Any], model_type: ModelType
) -> dict[str, Any]:
    """Map legacy/alternate model keys to GraphRag LanguageModelConfig fields."""
    normalized = dict(entry)
    if "type" not in normalized:
        normalized["type"] = model_type.value
    if model_type == ModelType.Chat and normalized.get("model_supports_json") is None:
        normalized["model_supports_json"] = True
    if "auth_method" in normalized and "auth_type" not in normalized:
        normalized["auth_type"] = normalized.pop("auth_method")
    retry = normalized.pop("retry", None)
    if isinstance(retry, dict) and "type" in retry and "retry_strategy" not in normalized:
        normalized["retry_strategy"] = retry["type"]
    return normalized


def _normalize_models(values: dict[str, Any]) -> None:
    """Merge completion_models / embedding_models into models."""
    if "models" in values and values["models"]:
        return

    models: dict[str, Any] = {}
    for model_id, entry in values.pop("completion_models", {}).items():
        if isinstance(entry, dict):
            models[model_id] = _normalize_language_model_entry(
                model_id, entry, ModelType.Chat
            )
    for model_id, entry in values.pop("embedding_models", {}).items():
        if isinstance(entry, dict):
            models[model_id] = _normalize_language_model_entry(
                model_id, entry, ModelType.Embedding
            )
    if models:
        if (
            defs.DEFAULT_CHAT_MODEL_ID not in models
            and "default_completion_model" in models
        ):
            models[defs.DEFAULT_CHAT_MODEL_ID] = models.pop("default_completion_model")
        values["models"] = models


def _normalize_input_output(values: dict[str, Any]) -> None:
    """Map input_storage / output_storage and legacy input.type."""
    if input_storage := values.pop("input_storage", None):
        input_config = values.setdefault("input", {})
        if not isinstance(input_config, dict):
            input_config = {}
            values["input"] = input_config
        input_config["storage"] = input_storage

    input_config = values.get("input")
    if isinstance(input_config, dict):
        if "type" in input_config and "file_type" not in input_config:
            input_config["file_type"] = input_config.pop("type")

    if output_storage := values.pop("output_storage", None):
        values["output"] = output_storage


def _normalize_vector_store(values: dict[str, Any]) -> None:
    """Wrap flat vector_store settings into the expected dict-of-stores shape."""
    vector_store = values.get("vector_store")
    if not isinstance(vector_store, dict):
        return
    if any(isinstance(v, dict) for v in vector_store.values()):
        return
    if "type" in vector_store or "db_uri" in vector_store:
        values["vector_store"] = {
            defs.DEFAULT_VECTOR_STORE_ID: vector_store,
        }


def _rename_key(section: dict[str, Any], old_key: str, new_key: str) -> None:
    if old_key in section and new_key not in section:
        section[new_key] = section.pop(old_key)


def _normalize_model_id(value: str) -> str:
    if value == "default_completion_model":
        return defs.DEFAULT_CHAT_MODEL_ID
    return value


def _normalize_workflow_sections(values: dict[str, Any]) -> None:
    """Map completion_model_id / embedding_model_id to current field names."""
    for section_name in _WORKFLOW_MODEL_ID_SECTIONS:
        section = values.get(section_name)
        if isinstance(section, dict):
            _rename_key(section, "completion_model_id", "model_id")
            if isinstance(section.get("model_id"), str):
                section["model_id"] = _normalize_model_id(section["model_id"])

    embed_text = values.get("embed_text")
    if isinstance(embed_text, dict):
        _rename_key(embed_text, "embedding_model_id", "model_id")

    for section_name in _SEARCH_CHAT_MODEL_SECTIONS:
        section = values.get(section_name)
        if isinstance(section, dict):
            _rename_key(section, "completion_model_id", "chat_model_id")
            if isinstance(section.get("chat_model_id"), str):
                section["chat_model_id"] = _normalize_model_id(section["chat_model_id"])


def _normalize_cache(values: dict[str, Any]) -> None:
    """Flatten nested cache.storage and map legacy cache.type values."""
    cache = values.get("cache")
    if not isinstance(cache, dict):
        return
    storage = cache.pop("storage", None)
    if isinstance(storage, dict) and storage.get("base_dir") and not cache.get("base_dir"):
        cache["base_dir"] = storage["base_dir"]
    if cache.get("type") == "json":
        cache["type"] = "file"


def normalize_graphrag_config_dict(values: dict[str, Any]) -> dict[str, Any]:
    """Normalize legacy or alternate settings.yaml keys before validation."""
    normalized = deepcopy(values)
    _normalize_models(normalized)
    _normalize_input_output(normalized)
    _normalize_vector_store(normalized)
    _normalize_workflow_sections(normalized)
    _normalize_cache(normalized)
    return normalized


def create_graphrag_config(
    values: dict[str, Any] | None = None,
    root_dir: str | None = None,
) -> GraphRagConfig:
    """Load Configuration Parameters from a dictionary.

    Parameters
    ----------
    values : dict[str, Any] | None
        Dictionary of configuration values to pass into pydantic model.
    root_dir : str | None
        Root directory for the project.
    skip_validation : bool
        Skip pydantic model validation of the configuration.
        This is useful for testing and mocking purposes but
        should not be used in the core code or API.

    Returns
    -------
    GraphRagConfig
        The configuration object.

    Raises
    ------
    ValidationError
        If the configuration values do not satisfy pydantic validation.
    """
    values = values or {}
    if root_dir:
        root_path = Path(root_dir).resolve()
        values["root_dir"] = str(root_path)
    normalized = normalize_graphrag_config_dict(values)
    return GraphRagConfig.model_validate(normalized)
