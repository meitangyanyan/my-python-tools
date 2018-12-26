#/usr/bin/env python
#-*- coding:utf-8 -*-
#Authot:Zhang Yan
#python3.x

class SSH:
    def __init__(self,ip,port,user,passwd="",ssh_key=""):
        import paramiko
        self.passwd=passwd
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        if ssh_key != "":
            pkey = ssh_key
            key = paramiko.RSAKey.from_private_key_file(pkey)
            self.client.connect(hostname=ip, port=port, username=user, pkey=key)
        else:
            self.client.connect(hostname=ip, port=port, username=user, password=passwd, timeout=10)
    def ssh(self,cmd):
        run_msg={"status":"0","msg":""}  #"1"是成功  "0"是失败
        cmd="%s &> /tmp/cmdresult.txt ; echo $? >> /tmp/cmdresult.txt" % cmd
        # paramiko执行完之后有时候无法准确返回执行结果,所以将执行结果和$?的值都保存在文件中,通过$?来判断命令是否执行成功
        print("[INFO] 执行命令: %s" % cmd)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        if self.passwd != "":
            stdin.write("%s\n" % (self.passwd))  # 这两行是执行sudo命令要求输入密码时需要的
            stdin.flush()  # 执行普通命令的话不需要这两行
        else:
            print("[ERROR] 执行sudo需要输入密码,但是未配置密码!")
        err = stderr.read().decode()
        if err != "":
            print("[ERROR] %s" % err)
        stdin, stdout, stderr = self.client.exec_command("cat /tmp/cmdresult.txt")
        out=stdout.read().decode().strip()
        status=out[-1]
        res=out[:-1]
        if status == "0":
            run_msg["status"]="1"
        run_msg["msg"] = res
        return run_msg
    def sftp(self,src_file,dest_file,put_flag=True):
        sftp_client = self.client.open_sftp()
        if put_flag:
            sftp_client.put(src_file,dest_file)
            print("[INFO] 上传 %s-->%s" % (src_file,dest_file))
        else:
            sftp_client.get(src_file,dest_file)
            print("[INFO] 下载 %s-->%s" % (src_file, dest_file))
    def ssh_close(self):
        self.client.close()


