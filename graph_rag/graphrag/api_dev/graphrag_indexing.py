#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GraphRAG 索引 API 调用脚本（路径与 graphrag_prompt_tune.py 保持一致）
"""

import asyncio
import shutil
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=SyntaxWarning)

from utils import setup_logging
import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.config.enums import IndexingMethod
from graphrag.index.typing.pipeline_run_result import PipelineRunResult

# =========================================================================
# 路径锁定（与 graphrag_prompt_tune.py 相同）
# =========================================================================
API_DEV_ROOT = Path(__file__).resolve().parent
BASE_ROOT = API_DEV_ROOT.parent.parent

# ========================================
# 用户配置参数
# ========================================

DATA_DIR_NAME = "test_pdf"
INDEX_METHOD = "Standard"
IS_UPDATE = False
MEMORY_PROFILE = False
OUTPUT_DIR = None
USE_TUNED_PROMPTS = True

PROMPT_OUTPUT_DIR = API_DEV_ROOT / "prompt_output"
PROMPT_FILE_MAPPING = {
    "extract_graph.txt": "prompts/extract_graph.txt",
    "summarize_descriptions.txt": "prompts/summarize_descriptions.txt",
    "community_report_graph.txt": "prompts/community_report_graph.txt",
}

logger = None


def apply_tuned_prompts(data_dir_path: Path) -> None:
    """将 api_dev/prompt_output 中的定制提示词同步到数据目录 prompts/。"""
    if not USE_TUNED_PROMPTS:
        logger.info("已关闭定制提示词，使用 %s/prompts 默认配置", data_dir_path)
        return

    if not PROMPT_OUTPUT_DIR.exists():
        logger.warning(
            "未找到 %s，将使用 %s/prompts 默认提示词",
            PROMPT_OUTPUT_DIR,
            data_dir_path,
        )
        return

    applied = 0
    for src_name, rel_dest in PROMPT_FILE_MAPPING.items():
        src = PROMPT_OUTPUT_DIR / src_name
        dest = data_dir_path / rel_dest
        if not src.exists():
            logger.warning("跳过缺失的提示词文件: %s", src)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        applied += 1
        logger.info("已应用定制提示词: %s -> %s", src, dest)

    if applied == 0:
        logger.warning("prompt_output 中无可用提示词，将使用默认 prompts")
    else:
        logger.info("共应用 %d 个定制提示词", applied)


async def run_indexing() -> list[PipelineRunResult]:
    data_dir_path = BASE_ROOT / DATA_DIR_NAME
    log_dir_path = data_dir_path / "logs"

    global logger
    logger = setup_logging(
        log_dir_path,
        log_file="dev_graphrag_indexing.log",
        logger_name="dev-graphrag-indexing",
    )

    logger.info("项目根目录: %s", BASE_ROOT)
    logger.info("数据目录: %s", data_dir_path)
    logger.info("定制提示词目录: %s", PROMPT_OUTPUT_DIR)
    logger.info("日志目录: %s", log_dir_path)
    logger.info("索引方法: %s", INDEX_METHOD)
    logger.info("增量更新: %s", "是" if IS_UPDATE else "否")
    logger.info("内存分析: %s", "是" if MEMORY_PROFILE else "否")

    if not (data_dir_path / "settings.yaml").exists():
        raise FileNotFoundError(f"未找到配置文件: {data_dir_path / 'settings.yaml'}")

    apply_tuned_prompts(data_dir_path)

    config_overrides: dict[str, str] = {}
    if OUTPUT_DIR:
        logger.info("使用指定输出目录: %s", OUTPUT_DIR)
        config_overrides["output.base_dir"] = OUTPUT_DIR
        config_overrides["reporting.base_dir"] = OUTPUT_DIR
        config_overrides["update_index_output.base_dir"] = OUTPUT_DIR

    graphrag_config = load_config(data_dir_path, None, config_overrides)

    logger.info("开始构建索引...")

    method = IndexingMethod.Fast if INDEX_METHOD.lower() == "fast" else IndexingMethod.Standard

    index_result = await api.build_index(
        config=graphrag_config,
        method=method,
        is_update_run=IS_UPDATE,
        memory_profile=MEMORY_PROFILE,
    )

    logger.info("索引构建完成，处理结果:")
    for workflow_result in index_result:
        status = f"错误\n{workflow_result.errors}" if workflow_result.errors else "成功"
        logger.info("工作流名称: %s\t状态: %s", workflow_result.workflow, status)

    return index_result


def main():
    try:
        asyncio.run(run_indexing())
        log_path = BASE_ROOT / DATA_DIR_NAME / "logs" / "dev_graphrag_indexing.log"
        output_path = BASE_ROOT / DATA_DIR_NAME / "output"
        print(f"索引构建完成，日志: {log_path}")
        print(f"索引输出: {output_path}")
    except Exception as e:
        print(f"运行错误: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
