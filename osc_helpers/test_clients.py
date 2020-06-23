import clients

ips = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '172.17.0.2',
    # 'host.docker.internal'
]

port = 5020

for ip in ips:
    print('Testing {}:{}'.format(ip, port))
    clients.test_client((ip, port))

