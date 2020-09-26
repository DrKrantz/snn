import socket


target_ip = '192.168.0.112'
receiving_ip = ''

target_port = 5000
receiving_port = 5000


def send(sock, ip):
    sock.sendto(b'uwe', (ip, target_port))


def listen(sock, address):
    sock.bind(address)
    while True:
        data, addr = sock.recvfrom(8)
        if data:
            print(data)
        else:
            print('Nothing')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('type')
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if args.type == 'send':
        send(sock, target_ip)
    elif args.type == 'listen':
        listen(sock, (receiving_ip, receiving_port))
