# 测试模块内 可以导入项目中任何其他模块内的内容
import pytest

from pkg.response import HttpCode


# 测试类
class TestAppHandler:
    # 简单测试
    def test_example(self):
        print('test_example')
        # 测试:某个操作的结果是否符合预期值,以及查看运行过程中是否会抛出异常
        # 断言 成立则通过 不成立则抛异常
        assert 1==1

    # 测试项目中的视图函数  调用接口
    # 会从@pytest.fixture 自动导入client
    def test_debug(self,client):
        print('test_example')

        # 正确访问测试
        '''
        response = client.post(
            "/apps/607c32d8-a5fb-44a6-bbce-c4eec061c2aa/debug",
            json={"query":"你好请介绍LLM的发展历史?"}
        )
        print("response:",response.json)
        # 断言
        assert response.status_code == 200
        assert response.json.get("code") == HttpCode.SUCCESS
        '''

        # 错误访问测试
        response = client.post(
            "/apps/607c32d8-a5fb-44a6-bbce-c4eec061c2aa/debug",
            json={"query": None}
        )
        print("response:", response.json)
        # 断言
        assert response.status_code == 200
        assert response.json.get("code") == HttpCode.SUCCESS


    # 一次性测试多组参数
    # 使用列表参数传递简化上述两段测试,如果有多个参数改为元组
    @pytest.mark.parametrize("query",["你好你是谁?",None])
    def test_debug_2(self,query,client):
        print('test_debug_2')
        resp = client.post(
            '/apps/607c32d8-a5fb-44a6-bbce-c4eec061c2aa/debug',
            json={"query": query}
        )
        print("response:",resp.json)
        # 断言
        assert resp.status_code == 200
        # 根据query的不同情况做判断
        if query is None:
            assert resp.json.get("code") == HttpCode.VALIDATION_ERROR
        else:
            assert resp.json.get("code") == HttpCode.SUCCESS