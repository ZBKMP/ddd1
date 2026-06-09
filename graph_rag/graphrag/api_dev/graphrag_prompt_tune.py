"""
GraphRAG提示词自动生成脚本 - 路径强固版
"""
import asyncio
import shutil
import warnings
from pathlib import Path
import json

import pandas as pd

# 抑制不相关的警告
warnings.filterwarnings("ignore", category=SyntaxWarning)

# 导入我们的日志工具
from utils import setup_logging

import graphrag.api.prompt_tune as prompt_tune
from graphrag.config.enums import InputFileType
from graphrag.config.load_config import load_config
from graphrag.config.models.graph_rag_config import GraphRagConfig
from graphrag.prompt_tune.types import DocSelectionType

# =========================================================================
# 自动化路径锁定（无论你在哪个目录下执行，都能精准定位项目根目录）
# =========================================================================
API_DEV_ROOT = Path(__file__).resolve().parent
BASE_ROOT = API_DEV_ROOT.parent.parent

# ========================================
# 用户配置参数 - 只需关注业务变量
# ========================================

DATA_DIR_NAME = "test_pdf"
CHUNK_SIZE = 500
OVERLAP = 100
LIMIT = 5
SELECTION_METHOD = "random"
DOMAIN = "股票投资"
LANGUAGE = "Chinese"
MAX_TOKENS = 2000
DISCOVER_ENTITY_TYPES = True
MIN_EXAMPLES_REQUIRED = 2
N_SUBSET_MAX = 300
K = 15

# 文本来源优先级: pdf_output -> index output -> input -> 原始 settings 配置
PROMPT_TUNE_INPUT_DIR = "prompt_tune_input"

logger = None


def _stage_text_file(staging_dir: Path, filename: str, content: str) -> Path:
    target = staging_dir / filename
    target.write_text(content, encoding="utf-8")
    return target


def prepare_prompt_tune_config(
    graphrag_config: GraphRagConfig,
    data_dir_path: Path,
    logger,
) -> tuple[GraphRagConfig, list[Path]]:
    """为 prompt tune 准备可读文本输入，避免 PDF 远程解析依赖。"""
    staging_dir = data_dir_path / PROMPT_TUNE_INPUT_DIR
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    staged_files: list[Path] = []

    for md_path in sorted((data_dir_path / "pdf_output").glob("*.md")):
        target = staging_dir / f"{md_path.stem}.txt"
        shutil.copy2(md_path, target)
        staged_files.append(target)
        logger.info("使用 pdf_output 文本: %s", md_path)

    documents_parquet = data_dir_path / "output" / "documents.parquet"
    if documents_parquet.exists():
        documents = pd.read_parquet(documents_parquet)
        for idx, row in documents.iterrows():
            text = str(row.get("text", "")).strip()
            if not text or text.startswith("["):
                continue
            title = str(row.get("title", f"doc_{idx}"))
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)
            target = _stage_text_file(staging_dir, f"{safe_name}_{idx}.txt", text)
            if target not in staged_files:
                staged_files.append(target)
        logger.info("使用索引输出 documents.parquet, 有效文本数: %d", len(staged_files))

    input_dir = data_dir_path / "input"
    for pattern in ("**/*.txt", "**/*.md"):
        for path in sorted(input_dir.glob(pattern)):
            target = staging_dir / f"{path.stem}.txt"
            if path.suffix.lower() == ".md":
                shutil.copy2(path, target)
            else:
                shutil.copy2(path, target)
            if target not in staged_files:
                staged_files.append(target)
                logger.info("使用 input 文本: %s", path)

    if not staged_files:
        logger.warning(
            "未找到可复用的文本文件，将回退到 settings.yaml 原始输入配置（可能是 PDF 远程解析）。"
        )
        return graphrag_config, []

    tuned_config = graphrag_config.model_copy(deep=True)
    tuned_config.input.file_type = InputFileType.text
    tuned_config.input.file_pattern = r".*\.txt$"
    tuned_config.input.storage.base_dir = PROMPT_TUNE_INPUT_DIR
    logger.info(
        "已为 prompt tune 准备 %d 个文本文件，目录: %s",
        len(staged_files),
        staging_dir,
    )
    return tuned_config, staged_files


async def run_prompt_tune():
    project_dir_path = BASE_ROOT
    data_dir_path = BASE_ROOT / DATA_DIR_NAME
    output_dir_path = API_DEV_ROOT / "prompt_output"
    log_dir_path = data_dir_path / "logs"

    output_dir_path.mkdir(parents=True, exist_ok=True)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    global logger
    logger = setup_logging(
        log_dir_path,
        log_file="graphrag_prompt_tune.log",
        logger_name="dev-graphrag-prompt-tune",
    )

    logger.info("真实定位项目根目录: %s", project_dir_path)
    logger.info("真实定位数据目录: %s", data_dir_path)
    logger.info("真实定位输出目录: %s", output_dir_path)

    if not (data_dir_path / "settings.yaml").exists():
        raise FileNotFoundError(f"未在数据目录中找到 settings.yaml 配置: {data_dir_path}")

    graphrag_config = load_config(data_dir_path)
    graphrag_config, staged_files = prepare_prompt_tune_config(
        graphrag_config, data_dir_path, logger
    )

    doc_selection = DocSelectionType.RANDOM
    if SELECTION_METHOD.lower() == "auto":
        doc_selection = DocSelectionType.AUTO
    elif SELECTION_METHOD.lower() == "all":
        doc_selection = DocSelectionType.ALL
    elif SELECTION_METHOD.lower() == "top":
        doc_selection = DocSelectionType.TOP

    effective_limit = LIMIT
    if staged_files and effective_limit > len(staged_files):
        logger.warning(
            "LIMIT=%d 大于可用文本数 %d，将按文本数自动调整。",
            effective_limit,
            len(staged_files),
        )

    logger.info("开始生成提示词...")

    try:
        (
            extract_graph_prompt,
            entity_summarization_prompt,
            community_summarization_prompt,
        ) = await prompt_tune.generate_indexing_prompts(
            config=graphrag_config,
            chunk_size=CHUNK_SIZE,
            overlap=OVERLAP,
            limit=LIMIT,
            selection_method=doc_selection,
            domain=DOMAIN,
            language=LANGUAGE,
            max_tokens=MAX_TOKENS,
            discover_entity_types=DISCOVER_ENTITY_TYPES,
            min_examples_required=MIN_EXAMPLES_REQUIRED,
            n_subset_max=N_SUBSET_MAX,
            k=K,
            verbose=True,
        )

        logger.info("正在保存生成的定制提示词到 prompt_output 文件夹...")

        (output_dir_path / "extract_graph.txt").write_text(
            extract_graph_prompt, encoding="utf-8"
        )
        (output_dir_path / "summarize_descriptions.txt").write_text(
            entity_summarization_prompt, encoding="utf-8"
        )
        (output_dir_path / "community_report_graph.txt").write_text(
            community_summarization_prompt, encoding="utf-8"
        )

        metadata = {
            "domain": DOMAIN,
            "language": LANGUAGE,
            "chunk_size": CHUNK_SIZE,
            "overlap": OVERLAP,
            "limit": LIMIT,
            "selection_method": SELECTION_METHOD,
            "text_source": (
                str(data_dir_path / PROMPT_TUNE_INPUT_DIR)
                if staged_files
                else graphrag_config.input.file_type.value
            ),
            "files": [
                {"name": "extract_graph.txt", "description": "实体提取提示词"},
                {"name": "summarize_descriptions.txt", "description": "实体摘要提示词"},
                {
                    "name": "community_report_graph.txt",
                    "description": "社区摘要提示词",
                },
            ],
        }

        with open(output_dir_path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info("提示词生成成功，输出目录: %s", output_dir_path)
        return extract_graph_prompt, entity_summarization_prompt, community_summarization_prompt

    except Exception as e:
        logger.error("提示词生成过程中发生错误: %s", str(e), exc_info=True)
        raise


def main():
    try:
        asyncio.run(run_prompt_tune())
    except Exception as e:
        print(f"\n运行错误: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
