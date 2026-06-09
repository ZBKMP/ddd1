# 1.Model组件及使用
  Model组件的基本组成:
  Model是Langchain的核心组件,LangChain并没有自己的LLM,但提供了一个标准接口,
  用于封装不同类型的LLM交互,模型分为两种类型:
  a.LLM : 使用纯文本作为输入和输出的大语言模型
  b.ChatModel:使用聊天消息列表作为输入,并返回聊天消息的聊天模型
  LangChain中两种模型结构都可以接收PromptValue/str/消息列表作为输入参数,
  内部会根据模型类型自动转换成str或者是消息列表.
    
  ChatModel的官网解释:https://python.langchain.com/docs/concepts/chat_models/
  LLM的官网解释:https://python.langchain.com/docs/concepts/text_llms/
  
  调用大模型最常用的方法：invoke / batch / stream
  
  langchain支持的Model提供商:https://python.langchain.com/docs/integrations/providers/
  安装OpenAI: pip install langchain-openai  
  LLM:from langchain_openai import OpenAI
  ChatModel:from langchain_openai import ChatOpenAI
  OpenAI提供的模型类型:https://platform.openai.com/docs/models
  
  
  还可以在Components-Chat models找到更多的ChatModel:
  https://docs.langchain.com/oss/python/integrations/chat
  百度千帆:https://python.langchain.com/docs/integrations/chat/baidu_qianfan_endpoint/

  Message组件:
  LangChain中Message是消息组件,所有消息都具有type类型,content内容,response_metadata响应元数据.
  消息组件包含5种类型:SystemMessage,HumanMessage,AIMessage,FunctionMessage,ToolMessage
  类似于之前的消息提示模板,但没有Function模板与Tool模板,他们不能由提示模板产生,必须由函数/工具调用产生.


  Model组件示例: 
  1.LLM与ChatModel使用技巧
  2.Model批处理
  3.Model流式输出