# 1.基于ReACT架构的Agent智能体设计与实现
  1.1.Agent 概念和运行流程:
  在 LLM 应用中，如果我们知道用户输入所需的工具使用特定顺序时，使用 LCEL 表达式构建链应用非常有用，
  但是对于某一些特例，我们使用工具的次数与顺序取决于输入，在这种情况下，我们希望让 LLM 本身决定使用
  工具的次数和顺序，而Agent智能体能做到这一点。
  在 LangChain 中，Agent 是一个核心概念，它代表了一种能够利用语言模型（LLM）和其他工具来执行复杂
  任务的系统，Agent 设计的目的是为了处理那些语言模型可能无法直接解决的问题，尤其是当这些任务涉及到多
  个步骤或者需要外部数据源的情况。
  无论一个 Agent 设计得多么复杂，使用什么架构，最基础的工作流程其实都非常简单，只有 5 个步骤：
    1.输入理解：Agent 首先解析用户输入，理解其意图和需求。
    2.计划定制：基于对输入的理解，Agent 会定制一个执行计划，决定使用哪些工具和执行的顺序。
    3.工具调用：Agent 按照计划调用相应的工具，执行必要的操作。
    4.结果整合：收集所有工具返回的结果，进行整合和解析，形成最终的输出。
    5.反馈循环：如果任务没有完成或者需要进一步的消息，Agent 可以迭代上述过程直到满足条件为止
  
  对比前面我们学习的函数调用，其实Agent的运行流程非常接近，多了一步执行工具和观察结果的步骤，甚至在
  前面的课时中，我们其实已经实现了该流程，只是没有将代码封装到一起而已，所以，对于一个 Agent 来说，
  其组成模块包括 3 个部分：
    1.Tools：Agent可以访问的工具集，每个工具通常执行一个特定的功能。
    2.Executor：执行 Agent计划的逻辑。
    3.Prompt Templates：指导 Agent 如何理解和处理输入的模板，可以定制化以适应不同任务。
  
  在 LangChain v0.2.0 版本中，有两种实现 Agent 的技巧，一种使用的是传统Agent组件，一种使用
  LangGraph，传统Agent组件特别适合入门的开发者，所以在这一章中我们会使用该方式，下一章在考虑使用 
  LangGraph 创建更加复杂、灵活性和控制性更强的 Agent 应用。
  针对传统Agent组件，LangChain 团队封装了共计 8 种 Agent，不同的 Agent 适用于不同的聊天模型.
  Agent 类型文档链接：
    https://python.langchain.com/v0.1/docs/modules/agents/agent_types/
  
  1.2.ReACT 智能体运行流程与实现
  ReACT 是 LangChain 最早支持的 Agent 架构，ReACT =Reason+Action，即推理与行动，目前绝大部分
  Agent架构都是在 ReACT 架构上进行衍生的。
  在 LangChain 中，要想创建基于 ReACT 架构的智能体，其实也非常简单，导入AgentExecutor、
  create_react_agent，在实例化的时候，传递对应的工具+prompt即可，其中 ReACT架构的智能体prompt 
  是有要求的。
  ReACT prompt 文档：https://smith.langchain.com/hub/hwchase17/react
  
  1.3. ReACT 智能体的缺陷:
  
# 2.基于工具调用的智能体设计与实现
  2.1.工具调用智能体
  基于 ReACT 架构的智能体会将tools(工具描述)、agent_scratchpad(智能体草稿)、工具结果、推理等内容
  全部放到同一个prompt中，并通过提取LLM的规范输出来决定下一步的操作，这种模式会随着 LLM 输出的随机性，
  不同 LLM 性能的差异让程序变得异常脆弱。
  而且 ReACT 架构早期设计之初是针对LLM(文本补全模型)进行设计的，即传入一段话，让 LLM 补全其后续的
  文本，随着 LLM 的发展，消息设计更友好、结构化输出更稳定的函数调用、性能更强大的 ChatModel 发布了，
  可以考虑将 ReACT 迁移到基于聊天消息+工具调用的架构上，思想不变，但是使用更稳定的消息列表+工具调用。
  
  在上述的工具调用智能体Prompt中，输出规范会通过检测LLM是输出文本内容还是工具调用参数来判断下一步是
  什么，这样性能更加稳定，而且对于绝大部分LLM来说，工具调用支持一次性调用生成多个工具的参数，性能会
  更强。
  在 LangChain 中，其实也为基于工具调用的Agent封装了一个快速创建的方法
  create_tool_calling_agent()  和预设Prompt。
    LangChain hub 工具调用 Prompt 链接：
  https://smith.langchain.com/hub/hwchase17/openai-tools-agent
     基于工具调用的智能体文档：
  https://python.langchain.com/v0.1/docs/modules/agents/agent_types/tool_calling/
  
  2.2.实现示例
  在 LangChain 中，要实现工具调用Agent其实也非常简单，步骤其实和ReACT-Agent一模一样，创建好工具
  列表、Prompt、LLM(支持工具调用)，然后使用create_tool_calling_agent()创建智能体，接下来创建
  智能体执行者完成包装即可
  
# 3.内置的其他Agent类型介绍与上手
  3.1.内置的其他 Agent 介绍:
  在 LangChain v 0.2.0 版本之前封装了大量基于传统Agent组件的 Agent 智能体创建方法，这些组件的设计
  思路其实都是以推理-行动-观察为思想，不同类型的 Agent 会进行一些额外的扩展，例如记忆、外挂知识库、
  多角色、反思等。
  而LangChain中封装的Agent也是基于推理-行动-观察思想，并为不同类型的 LLM/ChatModel 设计了不同的
  运行流程与prompt，例如有些大语言模型擅长解读和回复 XML 类型的数据（Authropic），而有些模型擅长解
  读和回复 JSON 数据，而有些模型又擅长结构化输出，所以对于不同类型的模型，可以使用不同Agent创建方法
  来创建。
   LangChain 不同类型 Agent 文档：
  https://python.langchain.com/v0.1/docs/modules/agents/agent_types/xml_agent/
  以 XMLAgent 为例，创建和使用的技巧也非常简单，只需修改prompt与创建Agent的方法即可，其他的无需
  任何调整
  
  3.2.内置 Agent 的异同点:
  通过前几节课学习的ReACTAgent、工具调用Agent、XMLAgent示例演示，其实可以很容易发现这些 Agent
  的异同点，首先是相同点：
    1.所有Agent都拥有input、agent_scratchpad两个输入变量，表示原始问题和智能体草稿。
    2.所有Agent都是单Agent自我执行，无法与其他 Agent 进行相互协作。
    3.所有Agent都可以通过切换prompt与create_xxx_agent()方法快速切换 Agent 而无需修改大量代码。
    4.所有Agent设计思想都是基于推理-行动-观察，只是不同的 Prompt 有所差异。
    5.所有Agent都是使用同一个LLM进行推理与答案生成，并不支持多LLM分工。
    6.除了基于工具调用的Agent，其他类型的智能体要修改 Prompt 适配特定语言一般都需要同步修改输出
      解析器。
  有差异的地方也非常明显：
    1.不同Agent的提示词风格有所差异，有的Agent会将tools也填写到prompt中，有的使用文本提示，
      有的使用消息提示。
    2.不同Agent的输出解析器不一致，绝大部分取决于prompt的差异，有的支持多工具，有的不支持。
  不同Agent的输入编码方式不一致，绝大部分取决于prompt和LLM的差异，有的支持历史记忆输入，有的不支持。
  
# 4.AgentExecutor源码解析与Agent组件缺陷
  4.1.AgentExecutor 源码解析
  在 LangChain 中，无论是什么类型的 Agent（内置封装），都必须通过AgentExecutor来创建执行者才可以
  运行具有循环+工具执行的智能体，在智能体执行者的底层，实际操作是调用 Agent 智能体，执行它选择的
  操作/工具，将操作输出传递回 Agent，然后重复
  
  4.2.传统 Agent 组件的缺陷
  LangChain 封装的Agent和Agent执行者虽然解决了 LCEL 表达式创建的单链应用没法执行循环步骤的问题，
  对于一些简单类型的 Agent 智能体创建已经足够使用，但是仍然存在不少缺陷。
  假设我们要创建一个 Agent 应用，该 Agent 可以处理数学和物理问题，并由两个不同的 LLM 负责不同的
  模块，根据用户的提问使用不同的 LLM + 工具列表 + 线路来回答用户的问题，传统的 Agent 就无能为力了。
  其实除了上述的问题，传统 Agent 还存在不少缺陷，如下：
   1.只有循环步骤并没有条件步骤，一个 Agent 应用只能一条路走到黑，不能执行不同的路由；
   2.没法亦或者很难将多个Agent融合起来相互协作；
   3.因对 Prompt 与输出解析器的过度封装，导致要修改 Agent 内部的方案变得异常困难；
   4.无论是 Agent 还是 AgentExecutor，因其黑盒机制，无法在执行的过程中进行额外的干预；
  想对Agent进行扩展或者动态切换 LLM 难度非常大，例如添加记忆、切换LLM等.
  
  但是对于传统Agent组件来讲，我们还是需要去掌握，因为在复杂度较小的情况下，该思路还是非常值得借鉴的，
  但对于一些复杂应用就无能为力了，下一章我们会来学习 LangChain 的最后一块拼图——LangGraph，掌握
  利用 LangGraph 构建复杂应用的技巧及底层运行原理，并且在 LLMOps 项目中，将 LangGraph 与知识库
  、工具、审核、多用户/多应用、多模态输入输出等功能结合起来，在实战中感受 LangGraph + LECL 
  表达式带来的酣畅淋漓的体验。