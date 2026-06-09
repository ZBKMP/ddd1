# 1.Document组件与文档加载器的使用  从资源文件中获取文档信息
  Document 与文档加载器:
  Document 类是 LangChain 中的核心组件，这个类定义了一个文档对象的结构，涵盖了文本内容和相关的
  元数据，Document 也是文档加载器、文档分割器、向量数据库、检索器这几个组件之间交互传递的状态数据。
  在 LangChain 旧日版本中，Document还支持 lookup 检索功能，不过新版本下 Document 组件只拥有
  最基础的记录信息功能
           Document=page_content(页面内容)+metadata(元数据)
  在前面的课时中，我们通过手动输入输入的形式来创建数据，但是在 RAG 开发中，一般会读取特定来源的数据，
  而非手动录入数据，例如:本地 markdown 文件、HTML网页、PDF文档、DOC文档、URL链接等多种方式来加载
  数据，然后再将原始文档按照特定切割成特定大小的文档，最后再将数据存储到向量数据库中，很少会手动录入数据。
  所以在 RAG 应用外部，一般都会有一个额外的扩展，专门用于处理 读取数据-切割数据-存储数据 这个流程，
  并且这个流程非常耗时，例如上传一个30M的文档,需要执行加载/切割/文本嵌入,一般都会使用队列/异步进行处理.
  
  在新的架构流程中，文档加载器起到的作用就是从各式各样的数据中提取出相应的信息，并转换成标准的 
  Document 组件，从而屏蔽不同类型文件的读取差异。
  在 LangChain 中所有文档加载器的基类为 BaseLoader，封装了统一的5个方法:
    1.load()/aload():加载和异步加载文档，返回的数据为文档列表。
    2.load_and_split():传递分割器，加载并将大文档按照传入的分割器进行切割，
               返回的数据为分割后的文档列表。
    3.lazy_load()/alazy_load():懒加载和异步懒加载文档，返回的是一个迭代器，适用于传递的数据源
       有多份文档的情况，例如文件夹加载器，可以每次获得最新的加载文档，不需要等到所有文档都加载完毕。
  在 LangChain 中封装了几十种文档加载器，几乎所有的文件都可以使用这些加载器完成数据的读取，
  而不需要手动去封装.
  LangChain 文档加载器文档:
    https://imooc-langchain.shortvar.com/docs/integrations/document_loaders/
  
  TextLoader 使用技巧与源码解析:
  在 LangChain 中最简单的加载器组件就是 TextLoader，这个加载器可以加载一个文本文件
  (源码markdown、text 等存储成文本结构的文件，DOC并不是文本文件)，并把整个文件的内容读入到一个
  Document 对象中，同时为文档对象的 metadata 添加 source 字段用于记录源数据的来源信息。
  TextLoader 使用起来非常简单，传递对应的文本路径即可.
 
  TextLoader 源码底层主要通过 open 函数与对应的编码方式打开对应的文件，获取其内容，并将传递的
  路径信息复制到生成的文档示例中的 metadata 字段中，从而实现数据的快速加载。
  
  以TextLoader 为例，扩展到 LangChain 封装的其他文档加载器，使用技巧都是一模一样的，在实例化
  加载器的时候，传递对应的信息(文件路径、网址、目录等)，然后调用加载器的load()方法即可-键加载文档。

# 2.langchain内置文档加载器使用技巧
  高频内置文档加载器的使用技巧:
   1.Markdown文档加载器
     pip install unstructured
     pip install markdown
   2.Office文档加载器
     Excel: pip install openpyxl pandas  msoffcrypto-tools
     PPT: pip install python-magic python-pptx
     Word: pip install python-docx
   3.URL网页加载器

   4.通用文档加载器
     pip install libmagic

  
# 3.langchain自定义文档加载器
  自定义加载器使用技巧:
  对于一些企业的内部数据，例如数据库、API接口等定制化非常强的数据，如果使用通用的文档加载器进行提取，
  虽然可以提取记录到相应的信息，但是加载的数据格式或者样式大概率没法满足我们的需求这个时候就可以考虑
  实现自定义文档加载器。
  例如上节课使用的 WebBaseLoader 文档加载器加载慕课网首页的信息，会提取得到很多空白数据(空格、换行、
  Tab 等)，将这类数据通过分割存储到向量数据库中，会极大降低检索与生成的效率和正确性。

  在 LangChain 中实现自定义文档加载器非常简单，只需要继承 BaseLoader 基类，然后实现lazy_1oad()
  方法即可，如果该文档加载器有异步使用的场景，还需要实现 alazy_load()方法。

  文档加载器扩展思考:
     文档加载器=二进制数据读取+解析逻辑

# 4.Blob与BlobParse替代文档加载器
   LangChain 中的 Blob 方案:
   许多文档加载器都涉及到解析文件，此类加载器之间的差异通常源于文件解析方式，而不是文件加载方式。
   例如，你可以使用 open()函数来读取 PDF或 Markdown 文件的二进制内容，但是需要不同的解析逻辑来将
   二进制数据转换为文本。
   在 LangChain 中也提供了一个类似的解决方案 Blob，其灵感来源于 Blob webAPI规范(这是前端Web 
   浏览器中定义的相关规范)。
   该方案下有 Blob、BlobLoader和 BaseBlobParser 三个类，含义如下:
      1.Blob:LangChain 封装的数据对象，通过引用或值表示原始数据，该类提供一个接口，以表示不同形式
             具体化的二进制数据，使用该类可以有助于将数据加载器的开发与解析器耦合。
      2.BlobLoader:Blob 数据加载器，类似 DocumentLoader，不过 BlobLoader 被设计成可以加载
             任何数据(未来的规划,暂时未实现)
      3.BlobParser:Blob 数据解析器，用于将传入的 Blob 数据转换成文档列表。
   例如上节课的需求(加载对应的文本信息，其中每行数据都作为一个 Document 组件)，使用 Blob 的方案来
   实现，只需自定义一个解析器并实现 lazy_parser()方法即可.

   Blob 数据存储类:
   LangChain 中设计的 Blob 数据存储类和 B1ob webAPI规范 定义的类非常接近，拥有以下方法和属性:
   1.data:原始数据，支持存储字节、字符串数据。
   2.mimetype:文件的 mimetype 类型。
   3.encoding:文件的编码，默认值为 utf-8.
   4.path:文件的原始路径，支持传递字符串路径或者 Path 类。
   5.metadata:存储的元数据，一般都有 source 字段。
   6.source():只读函数/属性，用于返回数据的来源。
   7.as_string():将数据转换成字符串。
   8.as_bytes():将数据转换成字节数据。
   9.as_bytes_io():将数据转换成缓冲流字节数据。
   10.from_path():从对应的路径中加载 Blob 数据(文件)
   11.from_data():从对应的原始数据中加载 Blob 数据(非文件)。
   
   Blob 加载器:
   解析器封装了将二进制数据解析为 Document 组件所需的逻辑，而 Blob 加载器则封装了从给定存储位置
   加载 Blob 所需的逻辑。不过目前在 LangChain 中，只集成了一个 FilesystemBlobLoader，即文件
   系统二进制数据加载器。
   这个加载器可以加载传入文件夹下的特定文件.
   如果要实现一个 Blob 加载器,只需要继承 BlobLoader类，并实现 yield_blobs()方法即可.

   Blob 通用加载器:
   之前示例中，Blob 加载器与解析器是分开使用的，其实在LangChain 中还封装了一个由BlobLoader 
   与 BaseBlobParser 组成的类--GenericLoader，这个类旨在提供标准化的方法，让BlobLoader 
   使用更简单，不过目前也仅支持 FilesystemBlobLoader。

   整体来说，Blob 解决方案目前 LangChain 封装与集成得非常少，如果需要使用 Blob 的形式来加载文件，
   目前还需要大量编写加载文件与解析数据的逻辑，效率比较低，不过随着未来 LangChain 团队封装的 Blob 
   解析逻辑越来越多，会逐渐代替 DocumentLoader 的方案。对于目前的版本来说，大家只需要知道有这个
   东西即可。 


# 5.文档转换器与字符分割器
  DocumentTransformer组件:
  在 LangChain 中，使用 文档加载器 加载得到的文档一般来说存在着几个问题:原始文档太大、原始文档的数据
  格式不符合需求(需要英文但是只有中文)、原始文档的信息没有经过提炼等问题。
  如果将这类数据直接转换成向量并存储到数据库中，会导致在执行相似性搜索和RAG 的过程中，错误率大大提升。
  所以在 LLM 应用开发中，在加载完数据后，一般会执行多一步转换的过程，即将加载得到的文档列表进行转换，
  得到符合需求的 文档列表 。
  转换涵盖的操作就非常多，例如:文档切割、文档属性提取、文档翻译、HTML 转文本、重排、元数据标记等都属于
  转换。

  在 LangChain 中针对文档的转换也统一封装了一个基类 BaseDocumentTransformer，所有涉及到文档的
  转换的类均是该类的子类，将大块文档切割成 chunk 分块的文档分割器也是BaseDocumentTransformer
  的子类实现。
  BaseDocumentTransformer 基类封装了两个方法:
    1.transform_documents():抽象方法，传递文档列表，返回转换后的文档列表。
    2.atransform_documents():转换文档列表函数的异步实现，如果没有实现，则会委托
                            transform_documents()数实现。
  在 LangChain 中，文档转换组件分成了两类:文档分割器(使用频率高)、
                                     文档处理转换器(使用频率低，老版本写法)。
  并且目前 LangChain 团队已经将 文档分割器 这个高频使用的部分单独拆分成一个 Python 包，
  哪怕不使用 LangChain 框架本身进行开发，也可以使用其文本分割包，快速分割数据，在使用前必须执行以
  下命令安装: pip install -qU langchain-text-splitters
  对于文本分割器来说，除了继承 BaseDocumentTransformer，还单独设置了文本分割器基类Textsplitter,
  从而去实现更加丰富的功能. 

  字符分割器基础使用技巧:
  在文档分割器中，最简单的分割器就是一一字符串分割器，这个组件会基于给定的字符串进行分割，默认为 \n\n，
  并且在分割时会尽可能保证数据的连续性。分割出来每一块的长度是通过字符数来衡量的使用起来也非常简单，
  实例化 characterTextsplitter 需传递多个参数，信息如下:
     1.separator:分隔符，默认为\n\n。
     2.is_separator_regex:是否正则表达式，默认为 False。
     3.chunk_size:每块文档的内容大小，默认为 4000。
     4.chunk_overlap:块与块之间重叠的内容大小，默认为 200。
     5.length_function:计算文本长度的函数，默认为 1en。
     6.keep_separator:是否将分隔符保留到分割的块中，默认为False
     7.add_start_index:是否添加开始索引，默认为 False，如果是的话会在元数据中添加该切块的起点。
     8. strip_whitespace : 是否删除文档头尾的空白，默认为 True。
  如果想将文档切割为不超过500字符,并且每块之间文本重叠50个字符可以使用CharacterTextsplitter来实现.
  
  
  
# 6.递归字符文本分割器的使用与运行流程
   递归字符文本分割器:
   普通的字符文本分割器只能使用单个分隔符对文本内容进行划分，在划分的过程中，可能会出现文档块过小 
   或者 过大 的情况，这会让 RAG 变得不可控，例如:
    1.文档块可能会变得非常大，极端的情况下某个块的内容长度可能就超过了 LLM 的上下文长度限制这样
       这个文本块永远不会被引用到，相当于存储了数据，但是数据又丢失了。
    2.文档块可能会远远小于窗口大小，导致文档块的信息密度太低，块内容即使填充到 Prompt 中，
       LLM 也无法提取出有用的信息。
  那么有没有一种分割方案，可以解决这个问题呢?按照 分隔符 初次分割的时候，去检测块内容，如果太大就
  按照提供的 备选分隔符 二次分割，如果太小则合并前后的块，最后让所有的块内容长度都控制在指定的大小
  并尽可能接近呢?
  在 LangChain 中就为这种方案提供了一个分割器组件-- RecursiveCharacterTextsplitter，
  即递归字符串分割，这个分割器可以传递 一组分隔符 和 设定块内容大小，根据分隔符的优先顺序对文本进行
  预分割，然后将小块进行合并，将大块进行递归分割，直到获得所需块的大小，最终这些文档块的大小并不能
  完全相同，但是仍然会逼近指定长度。
  RecursiveCharacterTextSplitter 的分隔符参数默认为["\n\n"，"\n"，""，""]，即优先使用换
  两行的数据进行分割，然后在使用单个换行符，如果块内容还是太大，则使用空格，最后再拆分成单个字符。
  所以如果使用默认参数，这个字符文本分割器最后得到的文档块长度一定不会超过预设的大小，但是仍然会有
  小概率出现远小于的情况(目前也没有很好的解决方案)。
  RecursiveCharacterTextSplitter 底层的运行流程其实也非常简单，可以拆分成 预分割、
  大文档块递归分割、小文档块合并。
  对比普通的字符文本分割器， 递归字符文本分割器可以传递多个分隔符，并且根据不同分隔符的优先级来执行
  相应的分割。在 LangChain 中通过 RecursiveCharacterTextSplitter 类实现对文本的递归字符串
  分割

  衍生代码分割器:
  递归字符文本分割器的核心部分在于传递不同的分割符列表，通过不同的优先级的列表，可以实现一些复杂文件
  的拆分，例如在该分割器内部预先构建了大量的的分割列表，用于在特定的编程语言中拆分文本。
  支持的编程语言类型存储在 langchain_text_splitters.Language 枚举中

  要想查看给定语言的分隔符，可以使用
  RecursiveCharacterTextsplitter.get_separators_for_language()函数获取，
  例如查看 Python  语言的分隔符:
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
separators =RecursiveCharacterTextSplitter.get_separators_for_language(Language.PYTHON)
print(separators)
  输出:['\nclass ', '\ndef ', '\n\tdef ', '\n\n', '\n', ' ', '']

  可以从分隔符列表中看到 Python 文件的分割逻辑，优先将所有类都分割出来，然后分割函数，接下来分割类方法、
  模块语句等内容。
  要想使用这些 编程语言分隔符 其实非常简单，在构造分割器的时候传递即可，或者使用from_language()并
  传递编程语言枚举数据也可以实现，

  中文场景下的递归分割:
  RecursiveCharacterTextSplitter 默认配置的分隔符均是英文场合下的，在中文场合下，除了换行/空格，
  一般还有更加复杂的语句结束判断标识，例如:。、!、?等标识符，如果想更好去切割 中英可以考虑重设分隔符
  列表(或者继承该类进行重写)。
  不同符号的优先级如下:
    1.\n\n :换行两次优先级最高。
    2.\n :普通换行符优先级其次，一般切断后都不会导致上下文语义丢失。
    3.。|！|？:中文中句号、感叹号、问号一般都表示句子结束，也可以尝试切割。
    4.\.\s|\!\s|\?\s :对应到英文中就是点,感叹号,问号,并且标准的英文写法在这些符号后通常需要添加空格。
    5.；|;\s :其次就是中英文的分段，在英文分段后一般会添加空格;
    6.，|,\s :接下来优先级是中英文中的逗号，逗号一般都表示句子语义还未结束，所以一般不切割除非文本块
             仍然超过大小。
    7. :空格和空字符串是优先级最低的切割符号之一，特别是在英文场合中，有时候两个词才有意义,切割出来意义
       就不大，而空字符串则是优先级最低的切割符，空字符串会把中文切割成单个汉字在英文场合下切割成单个
       字母，几乎完全丢失语义。

   在 LLMOps 项目中，具体的文本分割逻辑由创建知识库的用户决定，所以 分隔符、 文档块大小 和 块重叠
   大小 均是通过外部传递，然后再生成 RecursiveCharacterTextSplitter 分割器，而文档加载器使用 
   扩展名+通用非结构化文件加载器 来实现
  
   
# 7.语义文档分割器与其他内容分割器
   语义文档分割器的使用与背景:
   在前面课时中使用的文档分割器都是使用 特定字符 对文本进行拆分，这种拆分模式虽然考虑了文档中的上下文
   切断的问题，但是并没有考虑句子之间的语义相似性，如果有一篇长文本，需要将其分割成语义相关的块，以便
   更好地理解和处理，这个时候可以使用 LangChain 中的 语义相似性分割器(SemanticChunker)来实现这个
   任务。
   语义相似性分割器 目前仍处于实验性，这个类目前位于 langchain_experimental包中
   (这个包中的多与方法未来极大概率会发生变更，需要谨慎使用)   
   pip install -Uqq langchain_experimental  实验性的包
   SemanticChunker 在使用上和其他的文档分割器存在一些差异，并且该类并没有继承Textsplitter，
   实例化参数含义如下:
      1.embeddings:文本嵌入模型，在该分类器底层使用向量的 余弦相似度 来识别语句之间的相似性。
      2.buffer_size:文本缓冲区大小，默认为1，即在计算相似性时，该文本会叠加前后各1条文本如果不够则
                    不叠加(例如第1条和最后1条)。
      3.add_start_index:是否添加起点索引，默认为 False。
      4.breakpoint_threshold_type:断点阈值类型，默认为 percentile 即百分位
      5.breakpoint_threshold_amount:端点阈值金额/得分。
      6.number_of_chunks:分割后的文档块个数，默认为 None。
      7.sentence_split_regex:句子切割正则，默认为(?<=[.?!])\s+，即以英文的点、问号、感叹号切割语句，
                             不同的文档需要传递不同的切割正则表达式。

   SemanticChunker 的原理其实非常简单，核心思想是将文档拆分成独立的每一句，接下来根据传递的缓冲大小前后
   拼接字符串，然后计算拼接后的新字符串的文本嵌入/向量，然后计算这些文本的相似度，并根据传入的分块数+断点
   类型计算得到一个阈值，最后将相似度超过某个阈值的合并到一起，从而实现相似度分割。
   目前在 SemanticChunker 底层检测相似度阈值的方法有4种:百分位数(默认)、标准差，四分位数、梯度 
   
   其他文档分割器的使用:
   除了上述的文档分割器，在 LangChain 中还封装了一些其他场合下的分割器(使用频率不高)，涵盖了:
   基于 HTML 标题/段的分割器、Markdown 标题分割器、递归JSON 分割器、基于Token 计数的分割器等，
   使用起来和字符文本分割器非常接近。
   LangChain 文档分割器翻译文档:https://imooc-langchain.shortvar.com/docs/how_to/#检索器

   A.HTML/Markdown 标题/段分割器:
     在 LangChain 中设计了针对 HTML 类型文档的分割器-- HTMLHeaderTextsplitter 与HTMLSectionSplitter，
     分割器的作用如下:
     1.HTMLHeaderTextsplitter:在 HTML文档中按照元素级别进行分割，查找出每一块文本的内容与其所有关联
              的标题，并为每个相关的标题块提供元数据(顺序往上逐层查找，直到找到所有嵌套层级的标题)。
     2.HTMLSectionSplitter:在 HTML 文档中按照元素级别进行分割，查找出每一块文本的内容及其副标题(顺序
              往上查找，找到最近的副标题则停止)。
   理解起来其实也非常简单，层级关系并不是嵌套，而是看目录导航，例如在课件的左侧可以看到对应的导航，
   分别是一级标题、二级标题和三级标题，这块内容在哪个标题内下使用，就可以看成是被嵌套到哪个标题下，
   和实际的 HTML层级没有任何关系。
   另外在 LangChain 中除了 HTML 类型的文档可以使用这套分割规则，Markdown 类的文件也有类似的分割规则，
   可以使用 Markdown 标题分割器-- MarkdownHeaderTextsplitter 完成同样的文档分割。
   详细文档:https://imooc-langchain.shortvar.com/docs/how_to/markdown_header_metadata_splitter/
   
   B.递归 JSON 分割器
   对于JSON 类的数据，在LangChain 中也封装了一个递归JSON分割器--RecursiveJsonSplitter，这个分割器会按
   照深度优先的方式遍历JSON 数据，并构建较小的JSON块，而且尽可能保持嵌套JSON 对象完整，但如果需要保持文档
   块大小在最小块大小和最大块大小之间则会将它们拆分。
   在JSON 数据中，如果值不是嵌套的JSON，而是一个非常大的字典，则不会对该字符串进行拆分，可以配合 递归字符文本
   分割器 强制性拆分字符串，确保块大小在限制的范围内。
   RecursiveJsonSplitter 的参数非常简单，只需传递 max_chunk_size 和 min_chunk_size(可选)即可。
   RecursiveJsonSplitter 分割器的运行流程其实也非常简单，这个分割器会按照 深度优先 的方式遍历整个JSON，
   即一层一层往下读取数据，然后将对应的数据提取生成一个新的JSON，直到数据大小接近块大小(极端情况下还是会超过
   预设的块大小，例如JSON 数据中的 Key 很长，亦或者 Value 很长，甚至出现单条数据就超过了预设大小)。
   所以如果要使用该分割器，一般会结合 RecursiveCharacterTextsplitter 降低单条数据超过预设大小的风险，
   思路就是将递归JSON 分割器生成的文档列表进行二次分割。

   C. 基于标记的分割器:
   对于大语言模型来说，上下文的长度计算应该通过 token 进行计算，而不是通过字符长度len()函数在,OpenAl的GPT模型中，
   一个汉字大约等于1.5个Token，一个单词为1个Token，所以使用len()函数可能会导致很大的误差，
   在 LLM 应用开发中，不同的模型对于 Token 的计算并不相同，但是可以使用 tiktoken 这个包来大致计算文本的 token数，
   误差也相对较小，首先安装 tiktoken 包，命令如下:   pip install -U tiktoken

   定义一个基于 tiktoken 的长度计算函数，然后将该函数传递给分割器的 1ength_function

   在 LangChain 中，除了传递 length_function 方法，还可以直接调用分割器的类方法from_tiktoken_encoder()来快速
   创建基于 tiktoken 分词器的文本分割器(确保分词器使用的模型和开发的 LLM 保持一致即可)，
    
   
# 8.自定义文档分割器
   自定义文档分割器:
   在 LangChain 中，如果内置的文档分割器均没办法完成需求，还可以根据特定的需求实现自定义文档分割器
   (一般极少)，实现的方法也非常简单，继承文本分割器基类 Textsplitter，在构造函数中传递相关参数，
   然后实现 split_text()方法即可。
   
   例如，实现一个根据传递的分隔符实现对文档进行片段划分，并且将分割出来的文档片段转换成 N个关
   键词的分割器，安装分词包： pip install jieba3k

   RAG 文档分割/分块总结:
   在前面的课时中，我们学习过 字符文本分割器、递归字符文本分割器、Htm1标题/段分割器、语义分割器等
   多种文本分割器类型，这也是目前 RAG 分块 Chunk的4种策略:
     1.固定大小分块:这是最常见的分块方法，通过设定块的大小和是否有重叠来决定分块。这种方法简单直接，
       不需要使用任何NLP库，因此计算成本低且易于使用，例如characterTextsplitter亦或者直接循环
       遍历固定大小拆分。
     2.基于结构的分块:常见的 HTML、MARKDOWN 格式，或者其他可以有明确结构格式的文档。这种可以借助
      “结构感知”对文档分块，充分利用文档文本意外的信息，类似 LangChain 中的
       HTMLHeaderTextSplitter等
    3.基于语义的分块:这种策略旨在确保每个分块包含尽可能多的语义独立信息。可以采用不同的方法，如标点
      符号、自然段落、或者NLTK、Spicy 等工具包来实现语义分块，或者 Embedding-based方法，
      例如LangChain中的SemanticChunker等
    4.递归分块:递归分块使用一组分隔符，以分层和迭代的方式将输入文本划分为更小的块。
      如果最初分割文本没有产生所需大小或结构的块，则该方法会继续递归地分割直到满足条件，
      例如LangChain 中的 RecursiveCharacterTextsplitter等。   
    这些策略各有优势和适用场景，选择合适的分块策略取决于具体的应用需求和数据特性。很遗憾，到目前为止
    还没有什么是最优的策略，但这也是很难有一个产品一统天下的原因。同时策略可以组合使用并不是一类文档
    只能用一种策略。
    对于一个 RAG 场景，分成四个主要阶段:预检索、检索、后检索 和生成，其中 分块 是 预检索阶段的策略，
    如果在 分块 阶段尝试了上述 4种策略均没有很好的效果，或许就不应该采用 RAG 的策略，而是使用 微调 
    的方式，让这部分知识成为模型永久的记忆，效果可能会更好!


   
# 9.非分割类型的文档转换器 问答转换器  翻译转换器 *** doctran模块有兼容性问题
   DocumentTransformer组件:
   在 LangChain 中，另一种非分割类型的文档转换器，这类转换器也是传递 文档列表 并返回 文档列表，
   一般是将某种文档按照需求转换成另外一种格式(例如:翻译文档、文档重排、HTML 转文本、文档元数据提取、
   文档转问答等)。
   这类文档转换器由于接收 文档列表，返回的也是 文档列表，所以可以在 LLM 应用中任何存在 文档列表的
   地方使用，例如下方的 LLM 应用架构流程图中的 文档加载、文档切割、 检索器检索 的环节交互数据都是 
   文档列表，所以这几个环节都可以添加文档转换器组件。
   在 LangChain 中，使用文档转换器技巧非常简单，按照对应组件的构造函数进行传参，然后调用
   transformer_documents 函数即可完成对文档的快速转换(每个转换器生成的格式不一样，需查看文档
   了解生成内容详情)。 
   LangChain 封装的文档转换器组件:
   https://imooc-langchain.shortvar.com/docs/integrations/document_transformers/

   问答转换器:
   在 RAG 的外挂知识库中，向量存储知识库中使用的文档通常以叙述或对话格式存储。但是，绝大部分用户的
   查询都是问题格式，所以如果我们在对文档进行向量化之前先将其转换为 问格式，可以在一定程度上增加检索
   相关文档的可能性，降低检索不相关文档的可能性。
   这个技巧也是 RAG 应用开发中常见的一种优化策略，即将原始数据转换成 QA 数据后进行存储，除此之外，
   对于绝大部分 LLM 的微调，使用的也是 QA问答数据 也可以考虑使用该问答转换器进行转换。
   在 LangChain 中封装了 Doctran 库并实现了 DoctranQATransformer 类可以快捷实现该功能，
   这个库底层使用 OpenAl 的函数回调来实现对问答数据的提取，首先安装该库:
       pip install doctran

# 10.VectorStore组件深入学习与检索方法  MMR最大边际相关性
   VectorStore 组件深入学习:
   考虑到目前市面上的向量数据库众多，每个数据库的操作方式也无统一标准，但是仍然存在着一些公共特征，
   LangChain 基于这些通用的特征封装了 vectorstore 基类，在这个基类下，可以将方法划分成6种:
   相似性搜索、最大边际相关性搜索 、通用搜索 、添加删除精确査找数据、 检索器、创建数据库
    1 带得分闽值的相似性搜索:
     在 LangChain 的相似性搜索中，无论结果多不匹配，只要向量数据库中存在数据，一定会查找出相应的
     结果，在 RAG 应用开发中，一般是将高相似文档插入到 Prompt 中，所以可以考虑添加一个 相似性得分
     阀值，超过该数值的部分才等同于有相似性。
     在 similarity_search_with_relevance_scores()函数中，可以传递 score_threshold阈值参数，
     过滤低于该得分的文档。
     对于 score_threshold 的具体数值，要看相似性搜索方法使用的逻辑、计算相似性得分的逻辑进行设置，
     并没有统一的标准，并且与向量数据库的数据大小也存在间接关系，数据集越大，检索出来的准确度相比少
     量数据会更准确。 
    2 as_retriever()检索器:
     在 LangChain 中，VectorStore 可以通过 as_retriever()方法转换成检索器，在as_retriever()
     中可以传递一下参数:
      1.search_type:
          搜索类型，支持similarity(基础相似性搜索)、similarity_score_threshold
          (携带相似性得分+阈值判断的相似性搜索)、mmr(最大边际相关性搜索)。
      2.search_kwargs:
          其他键值对搜索参数，类型为字典，例如:k、fi1ter、score_threshold、fetch_k、
          lambda_mult等，当搜索类型配置为similarity_score_threshold 后，必须添加 
          score_threshold 配置选项，否则会报错，参数的具体信息要看 search_type 类型对应的
          函数配合使用。
     并且由于检索器是 Runnable 可运行组件，所以可以使用 Runnable 组件的所有功能
     (组件替换、参数西置、重试、回退、并行等)。

   MMR 最大边际相关性:
   最大边际相关性(MMR，max_marginal_relevance_search)的基本思想是同时考量查询与文档的 相关度，
   以及文档之间的相似度。相关度确保返回结果对查询高度相关，相似度则鼓励不同语义的文档被包含进结果集。
   具体来说，它计算每个候选文档与查询的相关度，并减去与已经入选结果集的文档的最大相似度，这样更不
   相似的文档会有更高分。
   而在 LangChain 中MMR的实现过程和 FAISS 的 带过滤器的相似性搜索 非常接近，同样也是先执行相似性
   搜索，并得到一个远大于 k的结果列表，例如 fetch_k 条数据，然后对搜索得到的 fetch_k 条数据计算
   文档之间的相似度，通过加权得分找到最终的k条数据。
   简单来说，MMR就是在一大堆最相似的文档中查找最不相似的，从而保证结果多样化。
   所以 MMR 在保证查询准确的同时，尽可能提供 多样化结果，以增加信息检索的有效性和多样性.

   执行一个 MMR 最大边际相似性搜索需要的参数为:搜索语句、k条搜索结果数据 、fetch_k条中间数据、 
   多样性系数(0代表最大多样性，1代表最小多样性)，在 LangChain 中也是基于这个思想进行封装，
   max_marginal_relevance_search()函数的参数如下:
   1.query:搜索语句，类型为字符串，必填参数。
   2.k:搜索的结果条数，类型为整型，默认为 4。
   3.fetch_k:要传递给 MMR 算法的的文档数，默认为 20。
   4.lambda_mu1t:
       函数系数，数值范围从0-1，底层计算得分=lambda_mult*相关性 +(1 -lambda_mult)*相似性，
       所以0代表最大多样性、1 代表最小多样性。
   5.kwargs:其他传递给搜索方法的参数，例如 fi1ter 等，这个参数使用和相似性搜索类似，具体
             取决于使用的向量数据库。

   在 LangChain 封装的 VectorStore 组件中，内置了两种搜索策略:相似性搜索、最大边际相关性搜索
   这两种策略有不同的使用场景，一般来说 80%的场合使用相似性搜索都可以得到不错的效果，对于一些追求
   创新/创意/多样性的 RAG 场景，可以考虑使用 最大边际相关性搜索。

   在使用 相似性搜索 时，尽可能使用 similarity_search_with_relevance_scores()方法并传递
   阈值信息，确保在向量数据库数据较少的情况下，不将一些不相关的数据也检索出来，并且着重调试 得分
   闽值(score_threshold)，对于不同的文档/分割策略/向量数据库，得分阈值并不一致，需要经过调试
   才能得到一个相对比较正确的值(阈值过大检索不到内容，阈值过小容易检索到不相关内容)。


# 11.检索器组件深入学习与使用技巧
   BaseRetriever 检索器基类:
   在 LangChain 中，传递一段 query 并返回与这段文本相关联文档的组件被称为 检索器，并且LangChain 
   为所有检索器设计了一个基类--BaseRetriever，该类集成了 RunnableSerializable,所以该类是一个 
   Runnable 可运行组件，支持使用 Runnable 组件的所有配置，在 BaseRetriever 下封装了一些通用的方法.

   其中 get_relevance_documents()方法将在 0.3.0 版本开始被遗弃(老版本非 Runnable 写法)，使用检索器
   的技巧也非常简单，按照特定的规则创建好检索器后(通过 as_retriever()或者 构造函数)，调用 invoke()
   方法即可
   
   并且针对所有 向量数据库，LangChain 都配置了as_retriever()方法，便于快捷将向量数据库转换成检索器，
   不同的检索器传递的参数会有所差异，需要查看源码或者查看文档搭配使用
    
   VectorStoreRetriever 检索器:
   vectorstoreRetriever 是 BaseRetriever 的子类，这是一个专门针对向量数据库的基础检索器，
   在vectorstoreRetriever 的内部实现了_get_relevant_documents()方法，还定义了单独的属性:
        1.vectorstore:检索器归属的向量数据库。
        2.search_type:搜索类型。
        3.search_kwargs:搜索参数
   这些参数均来源于 as_retriever()或者在实例化类时传递的参数，由于该组件是一个 Runnable 可运行组件，
   所以可以使用configurable_fields()来修改类内部的参数。
   
   在 LCEL 表达式构建的链应用中，.with_config()可以通过链一起传递，或者是调用.invoke()函数是传递
   config+configurable 属性完成对配置信息的替换，所以在 RAG 应用开发中，可以对检索器配置好相应的
   选项，如果需要特定信息时传递运行配置即可，否则会运行默认配置信息。

   除此之外，Runnable 可运行组件的其他配置也可以轻松配置使用:
     1.使用 .configurable_alternatives()来实现对 向量数据库检索器 的替换;
     2.使用.with_retry()来实现对出现错误的重试;
     3.使用 .with_fa11backs()来实现对出现错误时的回退;
     4.使用.with_listeners()来实现对执行生命周期的监听,
     5.使用 .bind()来实现动态传递绑定时参数(不过对于 weaviate 向量数据库来说，目前没有效果)。

   .bind()函数会将相应的数据传递给.invoke()的 kwargs 参数，但是在 weaviate 的 invoke()中并没有用到 
   kwargs 参数，所以.bind()函数不会起到效果，要想传递搜索参数给 weaviate 的.invoke()方法只能通过 
   search_kwargs 进行传递。
        
# 12.内置的检索器与自定义检索器技巧
  内置检索与自定义:
  除了向量数据库检索器，在 LangChain 内部还集成了大量的第三方检索器，这些检索器功能格式，
  涵盖:维基百科搜索、Weaviate 混合搜索、Zep 检索器、ES 搜索 等，
  链接:https://imooc-langchain.shortvar.com/docs/integrations/retrievers/.
  
  不过由于这些内置检索器开发的时间较早，绝大部分都是在 Runnable 与LCEL 表达式出来之前发布
  的部分检索器可能并不是 Runnable 可运行组件，使用方法也有差异，使用前需要查阅文档进行使用。
  如果内置的检索器没法完成需求，可以考虑使用 自定义检索器，比方接入一个可以快速检索 百度网站
  的检索器
  
  在 LangChain 中实现自定义检索器的技巧其实非常简单，只需要继承 BaseRetriever 类，然后实现
  _get_relevant_documents()方法即可，从 query 到 list[document]的逻辑全部都在这个函数
  内部实现，异步的方法也可以不需要实现，底层会委托同步方法来执行
  
  对于检索器这个模块来说，正常只需要了解 向量数据库检索器 的相关使用技巧，对于其他的一些检索器
  知道怎么根据文档使用即可，特别是针对网络/爬虫的检索，目前被更好的方案逐步代替-- 
  工具回调(下一周学习的内容)。