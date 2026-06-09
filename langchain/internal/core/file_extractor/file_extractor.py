import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from injector import inject
from langchain_community.document_loaders import (
    UnstructuredExcelLoader, UnstructuredPDFLoader, UnstructuredMarkdownLoader, UnstructuredHTMLLoader,
    UnstructuredCSVLoader, UnstructuredPowerPointLoader, UnstructuredXMLLoader, Docx2txtLoader, UnstructuredFileLoader,
    TextLoader,
)

from internal.model import UploadFile
from internal.service import CosService
# langchain中的Document
from langchain_core.documents import Document as LCDocument


#  通用文件提取器
@inject
@dataclass
class FileExtractor:
    """文件提取器，用于将远程文件、upload_file记录
                             加载成LangChain对应的文档或字符串"""
    # 依赖注入
    cos_service: CosService

    # 根据UploadFile数据库记录 加载对应文档
    def load(
            self,
            # UploadFile数据库记录
            upload_file: UploadFile,
            # 是否返回文本列表,False返回langchian的Document对象列表
            return_text: bool = False,
            # 是否为非结构化的数据如PDF,压缩包等,结构化的数据如文本文件,MD文件等
            is_unstructured: bool = True,
    ) -> Union[list[LCDocument], str]:  # 结果可能是LangChain文档列表或字符串
        """加载传入的upload_file记录，返回LangChain文档列表或者字符串"""
        # 1.使用tempfile模块创建一个临时的文件夹,用于临时存储从云端下载的文件
        with tempfile.TemporaryDirectory() as temp_dir:
            # 2.构建一个临时文件路径
            # os.path.basename函数 : 获取文件路径最后的文件名
            file_path = os.path.join(
                temp_dir,
                os.path.basename(upload_file.key)
            )

            # 3.将对象存储中的文件下载到本地的临时文件路径
            self.cos_service.download_file(
                key=upload_file.key,
                target_file_path=file_path,
            )

            # 4 从文件保存临时路径中去加载文件 生成文档或字符串
            return self.load_form_file(
                file_path=file_path,
                return_text=return_text,
                is_unstructured=is_unstructured,
            )

    # 从文件保存临时路径中去加载文件 生成文档或字符串
    @classmethod
    def load_form_file(
            cls,
            file_path: str,
            return_text: bool = False,
            is_unstructured: bool = True,
    ) -> Union[list[LCDocument], str]:
        """从本地文件中加载数据，返回LangChain文档列表 或者 字符串"""

        # 1 获取文件的扩展名 以此决定需要使用哪种文件加载器
        file_extension = Path(file_path).suffix.lower()

        # 2 根据不同的文件扩展名去加载不同的加载器
        if file_extension in [".xlsx", ".xls"]:
            loader = UnstructuredExcelLoader(file_path)
        elif file_extension == ".pdf":
            loader = UnstructuredPDFLoader(file_path)
        elif file_extension in [".md", ".markdown"]:
            loader = UnstructuredMarkdownLoader(file_path)
        elif file_extension in [".htm", ".html"]:
            loader = UnstructuredHTMLLoader(file_path)
        elif file_extension == ".csv":
            loader = UnstructuredCSVLoader(file_path)
        elif file_extension in [".ppt", "pptx"]:
            loader = UnstructuredPowerPointLoader(file_path)
        elif file_extension == ".xml":
            loader = UnstructuredXMLLoader(file_path)
        elif file_extension == ".docx":
            loader = Docx2txtLoader(file_path)
        else:
            # 不在上述的类型之内,使用通用的非结构化文件加载器,
            #    如果指定为结构化文件则使用文本文件加载器
            loader = UnstructuredFileLoader(
                file_path
            ) if is_unstructured else TextLoader(file_path)

        # 3.返回加载的文档列表或者文本
        # 文本使用分隔符合并多个文档内容,需要文档列表则直接返回loader.load的结果
        # 如需要将多篇内容合并成文本,多个内容之间的分隔符
        delimiter = "\n\n"
        return delimiter.join(
            [ document.page_content for document in loader.load() ]
        ) if return_text else  loader.load()
