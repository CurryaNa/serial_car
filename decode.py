import json
import os


# n = int(input())
# m = int(input())

# def sum(num):
#     SUM =0
#     while(num!=0):
#         SUM+=num%10
#         num/=10
#     return SUM
#
# a = list(range(1,n+1))
# a.sort(key = sum)
# print(a[m-1])

# 从文件加载 参数
# temp = "1A7"
# temp = int(temp,16)
# temp1 = int("e9",16)
# temp2 = int("04",16)
# temp+=(temp1+temp2)
# res = hex(temp)[2:]
# res = res.rjust(4, "0")
# res = res[2:]
# print(res)

# n = int(input())
# a = list(map(int, input().split()))
# m = int(input())
# quers = []
# for _ in range(m):
#     l, r = map(int, input().split())
#     l -= 1
#     r -= 1
#     quers.append((l, r))
# diff = [0 for _ in range(n)]
# for l, r in quers:
#     diff[l] += 1
#     diff[r + 1] -= 1
# for i in range(1, n + 1):
#     diff[i] += diff[i - 1]
#
# origin_sum = 0
# for i in range(n):
#     tmp = a[i] * diff[i+1]
#     origin_sum += tmp
#
# a.sort()
# diff.sort()
# sum = 0
# for i in range(n):
#     tmp = a[i - 1] * diff[i]
#     sum += tmp
#
# print(sum - origin_sum)

# import math
#
# def check(num):
#     cnt = 0
#     for i in range(2, int(math.sqrt(num)) + 1):
#         if num % i == 0:
#             cnt += 1
#         while num % i == 0:
#             num /= i
#
#     if num > 1:
#         cnt += 1
#     return cnt
#
#
# n = int(input("请输入一个数"))
# print(check(n))
def load(file_name):
    if os.path.exists(file_name):
        f = open(file_name, encoding='utf-8')
        content = f.read()
        user_dic = json.loads(content)
        return user_dic

res = load("ins1.json")
speedlist =res["直道"]["des"]["速度列表"]
print(speedlist)