import queue
import time
import uuid
from queue import Queue
from typing import Generator
from uuid import UUID

from internal.core.agent.entities.queue_entity import AgentQueueEvent, QueueEvent
from internal.entity.conversation_entity import InvokeFrom


# 智能体队列管理器 包含针对事件与队列的基本操作函数
# 智能体向队列输出内容的常用过程   Flask主线程读取队列从队列中获取信息
class AgentQueueManager:
    """智能体队列管理器"""
    q: Queue  # 队列
    user_id: UUID  # 用户ID (AccountID,ApiKey)
    task_id: UUID  # 任务ID(一次对话可看成一个任务)
    invoke_from: InvokeFrom  # 会话调用来源

    #  构造函数，初始化智能体队列管理器
    def __init__(
            self,
            user_id: UUID,
            task_id: UUID,
            invoke_from: InvokeFrom,
    ) -> None:
        """构造函数，初始化智能体队列管理器"""
        # 1.初始化数据
        self.q = Queue()
        self.user_id = user_id
        self.task_id = task_id
        self.invoke_from = invoke_from

    # 监听队列,循环持续处理队列中的元素  返回生成器 用于流式输出
    def listen(self) -> Generator:
        """监听队列返回的生成器,用于流式输出 """
        # 1.定义基础数据记录超时时间、开始时间、最后一次ping通时间
        # 超时时间,如果一个请求在超时时间内还未结束,则认为超时,强制关闭
        listen_timeout = 600  # 可以写到queue_entity.py
        # 记录当前时间  开始计时及表示开始向前端输出内容
        start_time = time.time()
        # 最后一次ping通时间
        last_ping_time = 0

        # 2.创建循环队列执行死循环读取数据,直到超时或者数据读取完毕
        while True:
            # 过程中会读取队列内的数据,如果读出空,会抛出异常:queue.Empty
            try:
                # 3.从队列中提取数据并检测数据是否存在，如果存在则使用yield关键字返回
                # 1秒内若未get到数据则抛出异常queue.Empty
                item = self.q.get(timeout=1)
                # 如果取出的是空,则表示队列已经结束了,结束循环
                # 后续执行stop_listen方法时,会往队列加入None
                if item is None:
                    break
                yield item # AgentQueueEvent
            except queue.Empty:
                # 如果出现空队列异常 则再继续下一次循环,继续读取队列信息
                continue
            finally:
                # finally : 无论是否出现异常 都强制执行的代码
                # 4.计算当次从队列获取数据的总耗时 这一次循环操作的耗时 
                #  每次循环过程中  elapsed_time 一直再计时累加
                elapsed_time = time.time() - start_time

                # 5.每10秒发起一个ping请求  防止队列中长时间没有数据 而导致前后端连接中断
                # 如果总耗时整除10的结果大于最后一次ping通时间,则发起一次ping请求
                if elapsed_time // 10 > last_ping_time:
                    self.publish(AgentQueueEvent(
                        id=uuid.uuid4(),
                        task_id=self.task_id,
                        event=QueueEvent.PING,
                    ))
                    last_ping_time = elapsed_time // 10
                # 例如:总耗时达到11秒,整除10结果为1,大于last_ping_time初始值0,发起一次ping,
                #     接着到了21秒,整除10结果为2,大于last_ping_time的当前值1,发起一次ping,

                # 6.判断总耗时是否超时，如果超时则往队列中添加超时事件
                if elapsed_time >= listen_timeout:
                    self.publish(AgentQueueEvent(
                        id=uuid.uuid4(),
                        task_id=self.task_id,
                        event=QueueEvent.TIMEOUT,
                    ))


    # 发布事件信息到队列
    def publish(
            self,
            event: AgentQueueEvent
    ) -> None:
        """发布事件信息到队列"""
        # 1.将事件对象添加到队列中
        self.q.put(event)

        # 2.检测事件类型是否为需要停止的类型，
        #   涵盖STOP、ERROR、TIMEOUT、AGENT_END
        if (event.event in
                [QueueEvent.STOP,
                 QueueEvent.ERROR,
                 QueueEvent.TIMEOUT,
                 QueueEvent.AGENT_END]
        ):
            # 需要停止时,则执行停止监听方法
            self.stop_listen()

    # 停止监听队列信息
    def stop_listen(self) -> None:
        """停止监听队列信息"""
        # 往队列中添加一条None数据,listen方法中执行的死循环中,
        # 发现队列里取出的是None则会停止循环
        self.q.put(None)

    # 发布错误信息到队列 调用publish方法实现
    def publish_error(self, error:Exception) -> None:
        """发布错误信息到队列"""
        self.publish(AgentQueueEvent(
            id=uuid.uuid4(),
            task_id=self.task_id,
            event=QueueEvent.ERROR,
            observation=str(error),
        ))
