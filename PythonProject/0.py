import redis

# 1. 连接 Redis（默认端口 6379）
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 2. 存入一个字符串
r.set('name', 'Gemini')

# 3. 读取
print(r.get('name'))  # 输出: Gemini

# 4. 设置过期时间（10秒后自动消失，适合存验证码）
r.setex('code', 10, '1234')