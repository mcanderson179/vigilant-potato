import paramiko
import getpass
import sys

def ssh_command(ip, user, passwd, port):
#   This next line deals with socket management
    client = paramiko.SSHClient()
#   The next line is for warning the client if the key received from the server is untrusted
    client.set_missing_host_key_policy(paramiko.WarningPolicy())


    try:
        client.connect(ip, port, user, passwd)
    except Exception as e:
        print('Exception', e)
        sys.exit()

    try:
        stdin, stdout, stderr = client.exec_command(cmd)
        stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        print('Returned output: ')
        print(output)
    except Exception as e:
        client.close()
        sys.exit()
    client.close()





if __name__ == '__main__':
    ip = input('Enter server ip: ') or '192.168.1.203'
    port = input('Enter port or <CR>: ') or 22
    user = input('Username: ')
    passwd = getpass.getpass()

    cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, user, passwd, port)
