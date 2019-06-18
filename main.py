import asyncio
import socket
import ssl
import traceback
from _thread import start_new_thread

host = "localhost"
port = 8889

client_sockets = []
client_hashmap = {} #"ip": "login"

server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'


def get_ssl_context():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    context.load_verify_locations(cafile=client_certs)
    return context

def get_server_socket():
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(5)
    return server_socket

def get_client_data(conn):
    #function to change when protocol works
    return conn.recv(1024).decode()

def handle_client(conn, addr):
    data = get_client_data(conn)
    print(data)
    #checking type of data and handle specific request

async def run_server():
    context = get_ssl_context()
    server_socket = get_server_socket()
    while True:
        try:
            c, addr = server_socket.accept()
            conn = context.wrap_socket(c, server_side=True)
            client_sockets.append(conn)
            print('Connected to :', addr[0], ':', addr[1])
            start_new_thread(handle_client, (conn, addr,))
        except socket.error as e:
            traceback.print_tb(e)

loop = asyncio.get_event_loop()
loop.run_until_complete(run_server())
