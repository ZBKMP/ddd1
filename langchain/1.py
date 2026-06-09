"""
Neo4j 简单连接演示。

使用前请确保 Neo4j 已启动，并修改下方连接配置。
"""

from neo4j import GraphDatabase

# 连接配置（按实际环境修改）
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"


class Neo4jDemo:
    """Neo4j 基础操作演示。"""

    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self._driver.close()

    def verify_connectivity(self) -> None:
        """验证数据库连接是否可用。"""
        self._driver.verify_connectivity()
        print("Neo4j 连接成功")

    def create_sample_data(self) -> None:
        """创建示例节点与关系。"""
        with self._driver.session() as session:
            session.run(
                """
                MERGE (a:Person {name: $name_a})
                MERGE (b:Person {name: $name_b})
                MERGE (a)-[:KNOWS]->(b)
                """,
                name_a="Alice",
                name_b="Bob",
            )
        print("示例数据创建完成")

    def query_persons(self) -> None:
        """查询所有 Person 节点。"""
        with self._driver.session() as session:
            result = session.run("MATCH (p:Person) RETURN p.name AS name ORDER BY name")
            names = [record["name"] for record in result]
        print(f"Person 节点: {names}")


def main() -> None:
    demo = Neo4jDemo(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        demo.verify_connectivity()
        demo.create_sample_data()
        demo.query_persons()
    finally:
        demo.close()


if __name__ == "__main__":
    main()
