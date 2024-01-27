import socket
from _thread import *
from entities import Player, Fruit
import pickle

server = "127.0.0.1"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")


players = [Player(0,0,50,50,(255,0,0),1000,500), Player(100,100, 50,50, (0,0,255),1000,500)]
fruits = [Fruit(500,250,10,10,(0,255,0)), Fruit(0,0,50,50,(0,255,0))]

def threaded_client(conn, id):
    conn.send(pickle.dumps(players[id]))
    reply = {'player':None, 'fruits':fruits}
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[id] = data

            if not data:
                print("Disconnected")
                break
            elif currentPlayer==2:
                reply['player'] = players[(id+1)%2]

            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1