# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""CLI functions for the GraphRAG module."""

import argparse
import json
import time
from pathlib import Path

import typer

_DEBUG_LOG_PATH = Path(__file__).resolve().parents[2] / "debug-d938bd.log"
_CONFIG_NAMES = ("settings.yaml", "settings.yml", "settings.json")


def _agent_debug_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
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


def _has_project_config(directory: Path) -> bool:
    return any((directory / name).is_file() for name in _CONFIG_NAMES)


def resolve_project_root(root: Path) -> Path:
    """Resolve --root to an existing GraphRAG project directory.

    When the CLI is run from a subdirectory (e.g. the graphrag package folder),
    relative paths are also checked against the parent working directory.
    """
    cwd = Path.cwd()
    raw = Path(root)
    dir_name = raw.name if raw.name not in {".", ""} else None
    candidates: list[Path] = []

    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend([cwd / raw, cwd.parent / raw])
        if raw.parts and raw.parts[0] == ".":
            stripped = Path(*raw.parts[1:]) if len(raw.parts) > 1 else Path()
            if stripped.parts:
                candidates.extend([cwd / stripped, cwd.parent / stripped])

    # Typer may resolve --root before the callback; also search by directory name.
    if dir_name:
        for base in [cwd, cwd.parent, *list(cwd.parents)[:4]]:
            candidates.append(base / dir_name)

    if raw in (Path(), Path(".")) or str(raw) in {".", ""}:
        for base in [cwd, *cwd.parents]:
            if _has_project_config(base):
                candidates.insert(0, base)
                break

    # #region agent log
    _agent_debug_log(
        "A",
        "cli.py:resolve_project_root",
        "candidate paths",
        {"cwd": str(cwd), "input_root": str(raw), "candidates": [str(c) for c in candidates]},
    )
    # #endregion

    seen: set[str] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        resolved_key = str(resolved)
        if resolved_key in seen:
            continue
        seen.add(resolved_key)

        if not resolved.is_dir():
            continue

        if _has_project_config(resolved):
            # #region agent log
            _agent_debug_log(
                "B",
                "cli.py:resolve_project_root",
                "resolved with config",
                {"resolved": resolved_key},
            )
            # #endregion
            return resolved

    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_dir() and str(resolved) in seen:
            # #region agent log
            _agent_debug_log(
                "C",
                "cli.py:resolve_project_root",
                "resolved directory without config",
                {"resolved": str(resolved)},
            )
            # #endregion
            return resolved

    tried = "\n  ".join(sorted(seen)) or str(raw)
    # #region agent log
    _agent_debug_log(
        "D",
        "cli.py:resolve_project_root",
        "not found",
        {"tried": sorted(seen), "cwd": str(cwd)},
    )
    # #endregion
    raise typer.BadParameter(
        f"Project root not found: {root}\n"
        f"Searched:\n  {tried}\n"
        f"Current working directory: {cwd}\n"
        f"Hint: from the graphrag package folder use e.g. --root ../test_source, "
        f"or pass an absolute path to the project directory."
    )


def file_exist(path):
    """Check for file existence."""
    if not Path(path).is_file():
        msg = f"File not found: {path}"
        raise argparse.ArgumentTypeError(msg)
    return path


def dir_exist(path):
    """Check for directory existence."""
    if not Path(path).is_dir():
        msg = f"Directory not found: {path}"
        raise argparse.ArgumentTypeError(msg)
    return path


def output_has_index_tables(
    output_dir: Path,
    required_tables: tuple[str, ...],
) -> tuple[bool, list[str]]:
    """Return whether all required parquet tables exist under output_dir."""
    missing: list[str] = []
    for table in required_tables:
        if not (output_dir / f"{table}.parquet").is_file():
            missing.append(f"{table}.parquet")
    return len(missing) == 0, missing


def resolve_query_output_dir(
    project_root: Path,
    configured_output: Path,
    data_dir: Path | None = None,
    required_tables: tuple[str, ...] = (
        "entities",
        "relationships",
        "communities",
        "community_reports",
        "text_units",
    ),
) -> Path:
    """Pick an output directory that contains a complete index for query."""
    project_root = project_root.resolve()

    if data_dir is not None:
        resolved = Path(data_dir).resolve()
        ok, missing = output_has_index_tables(resolved, required_tables)
        # #region agent log
        _agent_debug_log(
            "E",
            "cli.py:resolve_query_output_dir",
            "explicit data_dir",
            {"data_dir": str(resolved), "ok": ok, "missing": missing},
        )
        # #endregion
        if not ok:
            raise typer.BadParameter(
                f"Index incomplete in --data directory: {resolved}\n"
                f"Missing: {', '.join(missing)}"
            )
        return resolved

    primary = Path(configured_output).resolve()
    ok, missing = output_has_index_tables(primary, required_tables)
    # #region agent log
    _agent_debug_log(
        "E",
        "cli.py:resolve_query_output_dir",
        "primary output check",
        {"primary": str(primary), "ok": ok, "missing": missing},
    )
    # #endregion
    if ok:
        return primary

    parent_output = (project_root.parent / "output").resolve()
    ok_parent, _ = output_has_index_tables(parent_output, required_tables)
    # #region agent log
    _agent_debug_log(
        "F",
        "cli.py:resolve_query_output_dir",
        "parent output check",
        {"parent_output": str(parent_output), "ok": ok_parent},
    )
    # #endregion
    if ok_parent:
        return parent_output

    raise typer.BadParameter(
        f"Index not ready for query.\n"
        f"Project root: {project_root}\n"
        f"Expected index tables in: {primary}\n"
        f"Missing: {', '.join(missing)}\n"
        f"Run indexing first, for example:\n"
        f"  graphrag index --root {project_root}\n"
        f"Or query a project that already has output parquet files, for example:\n"
        f"  graphrag query --root {project_root.parent} --method local --query \"...\""
    )


def redact(config: dict) -> str:
    """Sanitize secrets in a config object."""

    # Redact any sensitive configuration
    def redact_dict(config: dict) -> dict:
        if not isinstance(config, dict):
            return config

        result = {}
        for key, value in config.items():
            if key in {
                "api_key",
                "connection_string",
                "container_name",
                "organization",
            }:
                if value is not None:
                    result[key] = "==== REDACTED ===="
            elif isinstance(value, dict):
                result[key] = redact_dict(value)
            elif isinstance(value, list):
                result[key] = [redact_dict(i) for i in value]
            else:
                result[key] = value
        return result

    redacted_dict = redact_dict(config)
    return json.dumps(redacted_dict, indent=4)
