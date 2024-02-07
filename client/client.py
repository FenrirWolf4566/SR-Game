from shared import network

HOST_ADDR = ('localhost', 12345)

def on_receive(data):
    print(f'Received {data}')

def on_remote_close():
    print('Connection closed by server')

nw = network.create(HOST_ADDR, on_receive, on_remote_close)