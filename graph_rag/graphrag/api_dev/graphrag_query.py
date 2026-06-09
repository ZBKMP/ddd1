#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GraphRAG 查询 API 调用脚本（路径与 graphrag_prompt_tune.py / graphrag_indexing.py 保持一致）
"""

import asyncio
import json
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=SyntaxWarning)

from utils import setup_logging
import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.callbacks.noop_query_callbacks import NoopQueryCallbacks
from graphrag.utils.storage import load_table_from_storage
from graphrag.storage.file_pipeline_storage import FilePipelineStorage

# =========================================================================
# 路径锁定（与 graphrag_prompt_tune.py 相同）
# =========================================================================
API_DEV_ROOT = Path(__file__).resolve().parent
BASE_ROOT = API_DEV_ROOT.parent.parent

# ========================================
# 用户配置参数
# ========================================

DATA_DIR_NAME = "test_pdf"

QUERY = "这篇论文主要研究什么问题？使用了哪些方法？"
QUERY_TYPE = "local"
RESPONSE_TYPE = "text"
COMMUNITY_LEVEL = 0
DYNAMIC_COMMUNITY_SELECTION = False
OUTPUT_FILE = None

logger = None


async def run_query() -> tuple[str, dict]:
    data_dir_path = BASE_ROOT / DATA_DIR_NAME
    log_dir_path = data_dir_path / "logs"

    global logger
    logger = setup_logging(
        log_dir_path,
        log_file="graphrag_query.log",
        logger_name="dev-graphrag-query",
    )

    logger.info("项目根目录: %s", BASE_ROOT)
    logger.info("数据目录: %s", data_dir_path)
    logger.info("查询类型: %s", QUERY_TYPE)
    logger.info("查询内容: %s", QUERY)
    logger.info("社区级别: %s", COMMUNITY_LEVEL)
    logger.info("动态社区选择: %s", "是" if DYNAMIC_COMMUNITY_SELECTION else "否")

    if not (data_dir_path / "settings.yaml").exists():
        raise FileNotFoundError(f"未找到配置文件: {data_dir_path / 'settings.yaml'}")

    graphrag_config = load_config(data_dir_path)

    output_dir = Path(graphrag_config.output.base_dir)
    if not output_dir.is_absolute():
        output_dir = data_dir_path / output_dir

    if not output_dir.exists():
        raise FileNotFoundError(
            f"索引输出目录不存在: {output_dir}，请先运行 graphrag_indexing.py"
        )

    logger.info("使用索引输出目录: %s", output_dir)

    storage = FilePipelineStorage(base_dir=str(output_dir))

    try:
        entities = await load_table_from_storage("entities", storage)
        logger.info("已加载实体数据，共 %d 条记录", len(entities))

        text_units = await load_table_from_storage("text_units", storage)
        logger.info("已加载文本单元数据，共 %d 条记录", len(text_units))

        communities = await load_table_from_storage("communities", storage)
        logger.info("已加载社区数据，共 %d 条记录", len(communities))

        community_reports = await load_table_from_storage("community_reports", storage)
        logger.info("已加载社区报告数据，共 %d 条记录", len(community_reports))

        relationships = await load_table_from_storage("relationships", storage)
        logger.info("已加载关系数据，共 %d 条记录", len(relationships))

        try:
            covariates = await load_table_from_storage("covariates", storage)
            logger.info("已加载协变量数据，共 %d 条记录", len(covariates))
        except Exception:
            covariates = None
            logger.info("未找到协变量数据，将使用 None")

    except Exception as e:
        logger.error("加载数据文件时出错: %s", str(e), exc_info=True)
        raise

    callbacks = []
    context_data = {}

    def on_context(context):
        nonlocal context_data
        context_data = context

    local_callbacks = NoopQueryCallbacks()
    local_callbacks.on_context = on_context
    callbacks.append(local_callbacks)

    logger.info("开始执行查询...")

    query_type = QUERY_TYPE.lower()
    try:
        if query_type == "local":
            response, context = await api.local_search(
                config=graphrag_config,
                entities=entities,
                communities=communities,
                community_reports=community_reports,
                text_units=text_units,
                relationships=relationships,
                covariates=covariates,
                community_level=COMMUNITY_LEVEL,
                response_type=RESPONSE_TYPE,
                query=QUERY,
                callbacks=callbacks,
            )
        elif query_type == "global":
            response, context = await api.global_search(
                config=graphrag_config,
                entities=entities,
                communities=communities,
                community_reports=community_reports,
                community_level=COMMUNITY_LEVEL,
                dynamic_community_selection=DYNAMIC_COMMUNITY_SELECTION,
                response_type=RESPONSE_TYPE,
                query=QUERY,
                callbacks=callbacks,
            )
        elif query_type == "drift":
            response, context = await api.drift_search(
                config=graphrag_config,
                entities=entities,
                communities=communities,
                community_reports=community_reports,
                text_units=text_units,
                relationships=relationships,
                community_level=COMMUNITY_LEVEL,
                response_type=RESPONSE_TYPE,
                query=QUERY,
                callbacks=callbacks,
            )
        elif query_type == "basic":
            response, context = await api.basic_search(
                config=graphrag_config,
                text_units=text_units,
                query=QUERY,
                callbacks=callbacks,
            )
        else:
            raise ValueError(
                f"不支持的查询类型: {QUERY_TYPE}，支持: local, global, drift, basic"
            )

        logger.info("查询成功完成")
        return response, context

    except Exception as e:
        logger.error("查询过程中发生错误: %s", str(e), exc_info=True)
        raise


def main():
    try:
        response, context = asyncio.run(run_query())

        print("\n" + "=" * 50)
        print("查询结果:")
        print("=" * 50)
        print(response)
        print("=" * 50)

        if OUTPUT_FILE:
            output_path = Path(OUTPUT_FILE)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "query": QUERY,
                        "response": response,
                        "context": str(context),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            print(f"\n结果已保存到文件: {output_path}")

    except Exception as e:
        print(f"运行查询时发生错误: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
