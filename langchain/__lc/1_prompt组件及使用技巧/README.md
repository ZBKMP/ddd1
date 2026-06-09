# 1.langchain安装
  python -m pip install --upgrade pip==25.3
  pip install openai==1.107.2
  pip install langchain==0.3.27
  pip install langchain-community==0.3.29
  
  官网：https://python.langchain.com/docs/introduction/
  Tutorials 教程
  How-to guides 操作指南 
  Conceptual guide 解释说明
  API Reference API 参考

  翻译文档:http://imooc-langchain.shortvar.com/docs/introduction/

  GitHub Langchain 0.3 :
    https://github.com/langchain-ai/langchain/tree/langchain%3D%3D0.3.26/docs/docs
  Api References Langchian 0.3:
    https://reference.langchain.com/v0.3/python/
  
  OpenAI开发者官网 :https://platform.openai.com/docs/overview?lang=python
  openai快速入门文档:
https://platform.openai.com/docs/quickstart?desktop-os=windows&language=python
    

# 2.Prompt组件及使用
  Prompt组件的基本组成:
  大多数LLM通常会将用户输入添加到一个更大的文本中,称为提示模版Prompt.
  模板提供有关特定任务的附加上下文,Prompt是所有AI应用交互的起点.
  
  PromptTemplate:LangChain中主要使用的Prompt,按照template进行一定格式化,
                 针对Prompt进行变量处理以及提示词的组合.
  Selector:Prompt的二次封装,根据不同条件去选择不同提示词,使用范围较窄,应用较少. 
  
  LangChain中BasePromptTemplate的子组件:
                角色提示模板,消息占位符,文本提示模板,聊天消息提示模板,提示,消息等

  Prompt组件的格式化:
  Prompt组件中默认使用f-string来格式化变量,直接利用{}包裹变量或表达式,在字符串中插入表达式的值.

  Prompt使用示例:
   1.基础用法 2.字符串提示拼接 3.聊天提示拼接 4.复用提示模板
  
