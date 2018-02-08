# #!/usr/bin/env python3
# # Created by xuchao on 2017/3/2.
# import random
# d
# def bin_search(data_set, val):
#     low = 0
#     high = len(data_set) - 1
#     while low <= high:
#         mid = (low + high) // 2
#         if data_set[mid]['id'] == val:
#             return mid
#         elif data_set[mid]['id'] < val:
#             low = mid + 1
#         elif data_set[mid]['id'] > val:
#             high = mid - 1
#         else:
#             return
#
#
# def random_list(n):
#     result = []
#     ids = list(range(1001, 1001 + n))
#     a1 = ['高', '李', '王', '孙']
#     a2 = ['天', '好', '', '']
#     a3 = ['野', '封', '真', '杰']
#     for i in range(n):
#         age = random.randint(18, 60)
#         idn = ids[i]
#         name = random.choice(a1) + random.choice(a2) + random.choice(a3)
#         result.append({'age': age, 'id': idn, 'name': name})
#     return result
#
#
# a = random_list(5)
# s = bin_search(random_list(5), 1002)
# print(a[s])
#
# d=[{'name': 'eth1', 'macaddress': '08:00:27:01:f3:df', 'bonding': 0, 'ipaddress': '192.168.56.2',
#   'network': '192.168.56.255', 'model': 'unknown', 'netmask': '255.255.255.0'},
#  {'name': 'eth0', 'macaddress': '08:00:27:28:7e:4d', 'bonding': 0, 'ipaddress': '10.0.2.4', 'network': '10.0.2.255',
#   'model': 'unknown', 'netmask': '255.255.255.0'}]

import time
data = [1,2,3,3,3,4,4,4,4,4,4,4,5]


def sole(l,n):
    ret = []
    for v,i in enumerate(l):
        if i == n:
            ret.append(v)
    if len(ret) == 1:
        ret.append(ret[0])
    return ret[0::len(ret)-1]

print(sole(data,1))

data1 = [1,2,5,4]

def soso(l,n):
    for m,i in enumerate(l):
        if i > n:
            continue
        for u,v in enumerate(l[1:]):
            if i > v:
                continue
            if i+v == n:
                return (m,u+1)

print(soso(data1,6))
