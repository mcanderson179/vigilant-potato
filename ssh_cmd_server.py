import paramiko
import sys
import subprocess
import time
import socket
import os.path

# Use to display key as text
# import io

# creates a private key if none is found
try:
    if os.path.exists('private_key.key'):
        host_key = paramiko.RSAKey.from_private_key_file('private_key.key')
    else:
        host_key = paramiko.RSAKey.generate(4096)
        host_key.write_private_key_file('private_key.key')
except Exception as e:
    print('Exception: ', e)
    sys.exit()

class Server(paramiko.ServerInterface):

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def check_auth_password(self, username, password):
        if (username == 'test') and (password == 'user'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_exec_request(self, channel, command):
        print('Grabbing subprocess info...')
        cmd_output = subprocess.check_output(command.decode('utf-8'), shell = True)
        cmd_output = cmd_output.strip()
        channel.send(cmd_output)
        return True


def listener():

    # establish tcp socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Stops potential "address is currently in use error
    sock.bind(('', 2222))  # listening port

    print('Listening...')
    sock.listen(1)

    client, addr = sock.accept()  # Wait for remote connection

    # New transport: Created first and handles lower level details of SSH connection ie: Authentication.
    print('Opening new paramiko transport')
    t = paramiko.Transport(client)
    t.load_server_moduli()
    t.add_server_key(host_key)
    server = Server()
    print('Starting server...')
    t.start_server(server=server)

    # New channel: Handle data stream of SSH connection after being established ie: performs tasks
    chan = t.accept(10)
    print('Opening new paramiko channel...')
    if chan is None:
        print('No channel.')  # Maybe wrong credentials
    else:
        print('Channel Authenticated.')
        time.sleep(.1)  # Time for subprocess to finish

        chan.close()
        t.close()
        sock.close()
        print('Exiting...')


while True:
    try:
        listener()
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)
