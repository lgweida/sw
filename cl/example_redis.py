from upstash_redis import Redis

redis = Redis(url="https://creative-cardinal-50005.upstash.io", token="AcNVAAIncDI5ODM5OTcyMmZhOGU0YmNkODMzMzA4MDY4YjM3MzIyM3AyNTAwMDU")

redis.set("foo", "bar")
value = redis.get("foo")
print(value)
