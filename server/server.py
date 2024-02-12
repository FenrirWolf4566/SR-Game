import asyncio
import socket
import json
import base64

from shared import network

HOST_ADDR = ('localhost', 12345)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(HOST_ADDR)
server.listen()
print(f'Listening on {HOST_ADDR}')
server.setblocking(False)

tasks: list[asyncio.Task] = []

# Information on the different connected clients
networks: dict[network.Address, network.Network] = {}

# Information on game datas
player_size = 10
fruit_size = 5
velocity = 5

raw_identifiant_table = {} # perso id to 0/1/2/3
available_ids = []
players = [] # (id, score, x, y)
fruits = []# (x,y)
NB_MAX_PLAYER = 2

def set_game():
    """
    Initialize the game state
    """
    global raw_identifiant_table, available_ids, players, fruits, networks
    networks = {}
    raw_identifiant_table = {} # perso id to 0/1/2/3/...
    available_ids = [i for i in range(NB_MAX_PLAYER)]
    players = [[0,0,50,300],[1,0,750,300]] # (id, score, x, y)
    fruits = [(50,50),(400,50),(750,50),(225,175),(400,175),(575,175),(400,300),(225,425),(400,425),(575,425),(50,550),(225,550),(400,550),(575,550),(750,550)] # (x,y)

def borders_of_screen(x, y):
    """
    Make sure the player doesn't go out of the screen
    Send the coordinates after potential correction
    """
    try:
        good_x = x
        good_y = y
        if x-player_size < 0:
            good_x = player_size
        elif x+player_size > 800:
            good_x = 800-player_size
        if y-player_size < 0:
            good_y = player_size
        elif y+player_size > 600:
            good_y = 600-player_size
        return good_x, good_y
    except Exception as e:
        print(f'borders_of_screen : {e}')
        return x,y

def is_another_player_here(id_ref, x, y):
    """
    Make sure the player doesn't collide with another one
    """
    try:
        for p in players:
            if p[0] != id_ref:
                x_target = p[2]
                y_target = p[3]
                ecart = (abs(x_target-x)**2 + abs(y_target-y)**2)**0.5
                if ecart<(2*player_size):
                    return True
        return False
    except Exception as e:
        print(f'is_another_player_here : {e}')
        return False

def has_eaten_a_fruit(x, y):
    """
    Verify if a fruit has been eaten
    Remove the fruit if it's the case
    """
    try:
        for f in fruits:
            x_target = f[0]
            y_target = f[1]
            ecart = (abs(x_target-x)**2 + abs(y_target-y)**2)**0.5
            if ecart<(player_size + fruit_size):
                fruits.remove(f)
                return True
        return False
    except Exception as e:
        print(f'has_eaten_fruit : {e}')
        return False

def on_receive(instruction_b, raw_identifiant=None):
    """
    React to a player's position change
    """
    instruction = instruction_b.decode('utf-8')
    identifiant = raw_identifiant_table[raw_identifiant]
    next_x = players[identifiant][2]
    next_y = players[identifiant][3]
    if instruction=='quit':
        splitted = raw_identifiant.split(".")
        port = splitted[-1]
        ip_length = len(raw_identifiant) - len(port) - 1
        ip = raw_identifiant[:ip_length]
        on_remote_close((ip, int(port)))
        return
    elif instruction=='1':
        #UP
        next_y -= velocity
    elif instruction=='2':
        #DOWN
        next_y += velocity
    elif instruction=='3':
        #RIGHT
        next_x += velocity
    elif instruction=='4':
        #LEFT
        next_x -= velocity
    else:
        print(f"UNKNOWN INPUT")
    next_x, next_y = borders_of_screen(next_x, next_y)
    if not is_another_player_here(identifiant, next_x, next_y):
        players[identifiant][2] = next_x
        players[identifiant][3] = next_y
        if has_eaten_a_fruit(next_x, next_y):
            players[identifiant][1] += 1
    return

def on_remote_close(addr=None):
    """
    Reaction to a client disconnection
    """
    print(f'Connection closed by {addr}')
    try:
        raw_id = addr[0]+'.'+str(addr[1])
        identifiant = raw_identifiant_table[raw_id]
        del raw_identifiant_table[raw_id]
        networks.pop(addr)
        available_ids.append(identifiant)
        if len(available_ids)==2:
            set_game()
    except Exception as e:
        print(f'Failed with error : {e}')
    return

async def send_to_user(network):
    """
    Send the game state to a connected client
    """
    try:
        if len(available_ids)>0:
            # Waiting for a second connection, we only send the ID
            dico_to_send = {'id':raw_identifiant_table[network.get_raw_id()]}
        else:
            dico_to_send = {'players': players, 'fruits':fruits}
        json_datas = json.dumps(dico_to_send, indent = 2)
        b64_datas = base64.b64encode(json_datas.encode('utf-8'))
        await network.send(bytes(b64_datas))
    except Exception as err:
        print("AH : "+err)


async def finish_game():
    """
    Stop the game by sending the final scores to all connected clients
    """
    for nw in networks.values():
        try:
            dico_to_send = {'scores': players}
            json_datas = json.dumps(dico_to_send, indent = 2)
            b64_datas = base64.b64encode(json_datas.encode('utf-8'))
            await nw.send(bytes(b64_datas))
            nw.stop()
        except Exception as e:
            print(f'Error during finish_game : {e}')
    set_game()

async def broadcast_update():
    """
    Send the updated game state to all connected clients
    """
    run = True
    while run:
        try:
            await asyncio.sleep(0.04) # 25 fps
            if len(fruits)==0:
                await finish_game()
            else:
                for nw in networks.values():
                    await send_to_user(nw)
        except asyncio.CancelledError:
            run = False

async def accept():
    loop = asyncio.get_running_loop()
    run = True
    while run:
        try:
            if len(available_ids) > 0:
                conn, addr = await loop.sock_accept(server)
                print(f'Accepted connection from {addr}')
                # Attribution de l'id
                raw = addr[0]+'.'+str(addr[1])
                identifiant = available_ids[0]
                raw_identifiant_table[raw] = identifiant
                
                nw = network.use_existing(conn, lambda data, raw=raw: on_receive(data,raw), lambda addr=addr: on_remote_close(addr))
                networks[addr] = nw
                nw.start()
                await send_to_user(nw)
                available_ids.remove(identifiant)
            else:
                await asyncio.sleep(0)
        except asyncio.CancelledError:
            run = False

async def serve():
    set_game()
    loop = asyncio.get_running_loop()
    tasks.append(loop.create_task(broadcast_update()))
    tasks.append(loop.create_task(accept()))
    await asyncio.wait(tasks)

def stop():
    for task in tasks:
        task.cancel()
    for nw in networks.values():
        nw.stop()
    server.close()
