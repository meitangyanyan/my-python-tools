#/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Ya
#python3.x

import base64

#加密
aa=base64.b64encode("nihao".encode(encoding="utf8"))
print(aa)
cc=base64.b64encode("你好".encode(encoding="utf8"))
print(cc)

#解密
bb=base64.b64decode(aa).decode(encoding="utf8")
print(bb)
dd=base64.b64decode(cc).decode(encoding="utf8")
print(dd)
