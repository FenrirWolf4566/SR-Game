from shared import network

HOST_ADDR = ('localhost', 12345)

def on_receive(data):
    try:
        list_str = data.decode("utf-8").split('|')
        list_tpl_str = [tuple(string[1:-1].split(',')) for string in list_str]
        print(f'3: {list_tpl_str}')
        print("\n\n")
    except Exception as e:
        print(f"FAILED WITH EXCEPTION : {e}")

def on_remote_close():
    print('Connection closed by server')

nw = network.create(HOST_ADDR, on_receive, on_remote_close)