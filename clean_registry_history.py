#!/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Yan
# python2/3

import urllib2,json,sys
from ssh_paramiko import SSH

#仓库目录
registry_dir="/data/registry/docker/registry/v2/"
#仓库地址url
registry_url="http://192.168.30.60:1179"
#仓库机器,在仓库机器上执行一些操作
ssh=SSH(ip="192.168.30.60",port=22,user="root",passwd="gXb@123!")

#参考链接:https://docs.docker.com/registry/spec/api/#listing-repositories 官方API
#API:GET /v2/_catalog 获取所有的仓库名
def get_registry_name_list():
    url = "%s/v2/_catalog?n=500" % registry_url

    headers = {"Content-type": "application/json"}
    request = urllib2.Request(url, headers=headers)

    response = urllib2.urlopen(request)

    result = json.loads(response.read())

    return result["repositories"]

#API: GET /v2/<name>/tags/list 获取指定仓库里的所有tag
def get_registry_tag_list(name):
    url = "%s/v2/%s/tags/list" % (registry_url,name)

    headers = {"Content-type": "application/json"}
    request = urllib2.Request(url, headers=headers)

    response = urllib2.urlopen(request)

    result = json.loads(response.read())
    print(result)
    return result["tags"]

#API: DELETE /v2/<name>/manifests/<reference>  删除指定仓库里的指定digest
def delete_registry(reference):
    url = "%s/v2/%s/manifests/sha256:%s" % (registry_url, name,reference)

    headers = {"Content-type": "application/json"}
    request = urllib2.Request(url, headers=headers)

    request.get_method = lambda: 'DELETE'
    try:
        urllib2.urlopen(request)
    except urllib2.URLError as err:
        print(err)



name_list=get_registry_name_list()
#tag=get_registry_tag_list("huikedu/kkb/kkb-qrcode-console")

# 元数据目录
metadataDirPrefix=registry_dir + "repositories/"
# 层数据目录
dataDir=registry_dir + "blobs/sha256"

if __name__ == '__main__':
    if name_list:
        for name in name_list:
            tag_list=get_registry_tag_list(name)
            # 要保留的digest,每个tag下面有current目录和index目录，
            # current目录下的link文件保存了该tag目前的manifest文件的sha256编码，
            # 而index目录则列出了该tag历史上传的所有版本的sha256编码信息。
            current_reference_list=[]
            # 要清除的digest,_revisions目录里存放了该仓库历史上上传版本的所有sha256编码信息,
            # 即该仓库下所有tag的历史版本.
            del_reference_list=[]
            revisions_dir="/tmp"
            if tag_list:
                for tag in tag_list:
                    current_f=metadataDirPrefix + name + "/_manifests/tags/" + tag + "/current/link"
                    current_res=ssh.ssh("cat %s" % current_f)
                    if current_res["status"] == "1":
                        current_reference=current_res["msg"].split(":")[1]
                        current_reference_list.append(current_reference)
                    else:
                        sys.exit(current_res["msg"])
                current_reference_str="|".join(current_reference_list)
                revisions_dir=metadataDirPrefix + name + "/_manifests/revisions/sha256"
                # 在_revisions目录中,除了该仓库下所有tag的current版本就是历史版本,所以用grep -vE
                del_res_exsit = ssh.ssh('''ls %s|grep -vE "%s"|wc -l''' % (revisions_dir, current_reference_str))
                if del_res_exsit["status"] == "1":
                    if del_res_exsit["msg"].encode(encoding="utf-8").strip() != "0":
                        del_res = ssh.ssh('''ls %s|grep -vE "%s"''' % (revisions_dir,current_reference_str))
                        if del_res["status"] == "1":
                            del_reference_list=del_res["msg"].strip().split("\n")
                        else:
                            sys.exit(del_res["msg"])
                        print(name)
                        print(del_reference_list)
                else:
                    sys.exit(del_res_exsit["msg"])

            if del_reference_list:
                for del_reference in del_reference_list:
                    delete_registry(del_reference)
                del_reference_str=",".join(del_reference_list)
                # 使用DELETE API没有删掉_revisions下的历史版本的目录,手动删除下,此脚本tags/index下的目录未删除
                del_reference_res=ssh.ssh("rm -rf %s/{%s}" % (revisions_dir,del_reference_str))

    # 使用DELETE API只是删除了元数据,实际的数据(层数据)并没有删除,要执行垃圾回收
    # 执行下面的命令真正释放空间:registry garbage-collect /etc/docker/registry/config.yml
    cmd="docker exec registry-srv registry garbage-collect /etc/docker/registry/config.yml"
    clean_res=ssh.ssh(cmd)
    if clean_res["status"] == "1":
        print("sucessful")





