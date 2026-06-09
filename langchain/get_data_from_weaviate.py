import weaviate

# 连接到本地的 Weaviate 实例
client = weaviate.connect_to_local(
            host="192.168.172.129",
            port=8080,
        )

try:
    # 定位数据集
    collection = client.collections.get("Llmops_dataset")
    # 查询数量
    response = collection.aggregate.over_all(total_count=True)
    total_count = response.total_count
    print(total_count)
    # 遍历该 collection 下的所有对象
    for item in collection.iterator():
        # 打印每个对象的 ID 和属性
        print(f"UUID: {item.uuid}, Properties: {item.properties}")

finally:
    # 确保关闭客户端连接
    client.close()