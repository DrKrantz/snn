import socket


sender_ip = 'host.docker.internal'
receiver_ip = ''

sender_port = 5000
receiver_port = 5000


def send(sock, ip):
    sock.sendto(b'uwe', (ip, sender_port))


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
        send(sock, sender_ip)
    elif args.type == 'listen':
        listen(sock, (receiver_ip, receiver_port))


