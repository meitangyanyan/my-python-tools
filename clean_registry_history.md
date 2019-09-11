# 脚本原理:
[docker registry目录结构解析](http://note.youdao.com/noteshare?id=b3dc50730505c3946c03ab33e1b948a4)

# 脚本使用说明:
> 此脚本通用性较强,可稍作修改直接使用,
支持python2.7和python3.x

> 有引用同仓库下的ssh_paramiko.py实现ssh操作

    #仓库目录
    registry_dir="/data/registry/docker/registry/v2/"
    #仓库地址url
    registry_url="http://192.168.30.60:1179"
    #仓库机器,在仓库机器上执行一些操作
    ssh=SSH(ip="192.168.30.60",port=22,user="root",passwd="xxxx")

执行脚本之前修改这三个参数!

> 注意1: 如果registry开启了缓存的话,需要清除缓存(缓存的元数据)

     storage:
       cache:
         blobdescriptor: inmemory

如上,我的registry的配置文件是开启的内存缓存,所以需要重启registry服务,如果大家开启的是redis的话,需要去redis中删除缓存!

> 注意2: registry配置文件需要开启delete-enabled-true,允许删除镜像

    storage:
      delete:
        enabled: true

这样才能使用垃圾回收删除镜像!