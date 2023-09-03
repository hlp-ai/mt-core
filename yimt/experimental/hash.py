import hashlib
import time


def get_hash(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


txt = "sdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsddfsdfsdfsdfdsfsdfsdf"

start = time.time()
for i in range(10000):
    h = get_hash(txt)

print(time.time() - start)
