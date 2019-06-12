import socket
import ssl

host = "localhost"
port = 8888

server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)

bindsocket = socket.socket()
bindsocket.bind((host, port))
bindsocket.listen(5)

while True:
    try:
        c, addr = bindsocket.accept()
        conn = context.wrap_socket(c, server_side=True)
        print('Connected to :', addr[0], ':', addr[1])
        print(conn.recv(1024).decode())
    except socket.error:
        print(socket.error)