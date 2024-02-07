import asyncio
from collections import namedtuple
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

networks: dict[network.Address, network.Network] = {}

player_size = 10
fruit_size = 5
velocity = 3

raw_identifiant_table = {} # perso id to 0/1/2/3
available_ids = [0,1]
players = [(1,1,1,1),(2,2,2,2)] # (id, score, x, y)
fruits = [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)] # (x,y)

def borders_of_screen(x, y):
    """
    Vérifie que les bordures de l'écran ne sont pas dépassées par le joueur
    Renvoit les coordonnées après correction éventuelle
    """
    good_x = x
    good_y = y
    if x < 0:
        good_x = 0
    elif x > 800:
        good_x = 800
    if y < 0:
        good_y = 0
    elif y > 600:
        good_y = 600
    return (good_x, good_y)

def is_another_player_here(id_ref, x, y):
    """
    Vérifie que le joueur n'entre pas en collision avec un autre
    """
    for p in players:
        if p[0] != id_ref:
            x_target = p[2]
            y_target = p[3]
            ecart = (abs(x_target-x)**2 + abs(y_target-y)**2)**0.5
            if ecart<(2*player_size):
                return True
    return False

def has_eaten_a_fruit(x, y):
    """
    Vérifie si un fruit a été mangé
    Retire le fruit si c'est le cas
    """
    for f in fruits:
        x_target = f[0]
        y_target = f[1]
        ecart = (abs(x_target-x)**2 + abs(y_target-y)**2)**0.5
        if ecart<(player_size + fruit_size):
            fruits.remove(f)
            return True
    return False

def on_receive(raw_identifiant, instruction_b):
    """
    Réagit au changement de position d'un joueur
    instruction = int(data.decode("utf-8"))
    """
    instruction = instruction_b.decode('utf-8')
    identifiant = raw_identifiant_table[raw_identifiant]
    x = players[identifiant][2]
    y = players[identifiant][3]
    print(f'{raw_identifiant} : {identifiant} ({x}:{y})')
    if instruction=='1':
        #UP
        print("UP")
        y -= velocity
    elif instruction=='2':
        #DOWN
        print("DOWN")
        y += velocity
    elif instruction=='3':
        #RIGHT
        print("RIGHT")
        x += velocity
    elif instruction=='4':
        #LEFT
        print("LEFT")
        x -= velocity
    else:
        print(f"UNKNOWN INPUT")

    x, y = borders_of_screen(x, y)
    if not is_another_player_here(identifiant, x, y):
        players[identifiant][2] = x
        players[identifiant][3] = y
        if has_eaten_a_fruit(x, y):
            players[identifiant][1] += 10
            
    return

def on_remote_close(addr=None):
    print(f'Connection closed by {addr}')
    networks.pop(addr)

async def send_to_user(network):
    try:
        if len(available_ids)>0:
            dico_to_send = {'id':raw_identifiant_table[network.get_raw_id()]}
        else:
            dico_to_send = {'players': players, 'fruits':fruits}
        print(dico_to_send)
        json_datas = json.dumps(dico_to_send, indent = 2)
        b64_datas = base64.b64encode(json_datas.encode('utf-8'))
        await network.send(bytes(b64_datas))
    except Exception as err:
        print(err)


async def broadcast_update():
    run = True
    while run:
        try:
            await asyncio.sleep(2)
            for nw in networks.values():
                await send_to_user(nw)
        except asyncio.CancelledError:
            run = False

async def accept():
    loop = asyncio.get_running_loop()
    run = True
    while run:
        try:
            conn, addr = await loop.sock_accept(server)
            print(f'Accepted connection from {addr}')
            if len(available_ids) > 0:
                # Attribution de l'id
                raw = addr[0]+'.'+str(addr[1])
                identifiant = available_ids[0]
                available_ids.remove(identifiant)
                raw_identifiant_table[raw] = identifiant

                nw = network.use_existing(conn, on_receive, lambda addr=addr: on_remote_close(addr))
                networks[addr] = nw
                nw.start()
        except asyncio.CancelledError:
            run = False

async def serve():
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
