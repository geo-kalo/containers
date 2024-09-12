import socket
import subprocess


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('0.0.0.0', 65432)  #
print(f'Starting up on {server_address[0]} port {server_address[1]}')
sock.bind(server_address)

sock.listen(1)

while True:
    print('Waiting for a connection...')
    connection, client_address = sock.accept()
    
    try:
        print(f'Connection from {client_address}')
        while True:
            data = connection.recv(2048)
            if data:
                print(f'Received data: {data.decode("utf-8")}')
                with open('/iptables', 'ab') as f:
                    f.write(data)
            else:
                print('No more data from', client_address)
                command = 'iptables-restore --test /iptables'
                restoration = subprocess.run(command, shell=True, capture_output=True, text=True)
                if restoration.returncode == 0:
                    command = 'iptables-restore /iptables'
                    restoration = subprocess.run(command, shell=True, capture_output=True, text=True)
                    print(restoration)
                    command = 'truncate -s0 /iptables'
                    wipe = subprocess.run(command, shell=True, capture_output=True, text=True)
 
                break
    finally:
        connection.close()




#cat iptables | nc -q0 192.168.199.2 65432 
#episis thelei nc se firewall kai webserice
