import weaviate

client = weaviate.connect_to_local(host="192.168.172.129", port=8080)

try:
    # 1. 获取所有 Collection 的名字
    collections_info = client.collections.list_all()

    print(f"{'Collection Name':<30} | {'Count':<10}")
    print("-" * 45)

    for name in collections_info.keys():
        col = client.collections.get(name)
        # 聚合查询每个集合的数量
        res = col.aggregate.over_all(total_count=True)
        count = res.total_count
        print(f"{name:<30} | {count:<10}")

finally:
    client.close()

