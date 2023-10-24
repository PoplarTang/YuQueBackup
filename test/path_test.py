import sys


# print(sys.argv)

# aa = "itheima/python"
# bb = sys.argv[1]

# print(aa.count("/"))
# print(bb.count("/"))
# print(bb)

repo_path = "https://www.yuque.com/yuque/developer/high_level_api"
paths = repo_path.split("/")[3:5]
print(paths)

repo_path = "https://www.yuque.com/yuque/developer"
paths = "/".join(repo_path.split("/")[3:5])
print(paths)
