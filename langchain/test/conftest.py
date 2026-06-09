import pytest
from app.http.app import app # 导入app对象以供测试

# 创建出在pytest模式下的接口测试 客户端
@pytest.fixture
def client():
    # 开启flask的测试模式
    app.config["TESTING"] = True
    # 获取测试的client对象
    with app.test_client() as client:
        # 使用yield相比return扩展性更好 后续还可增加其他代码
        yield client  #返回flask应用的测试环境