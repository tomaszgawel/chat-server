import socket
import ssl

# TEST CLIENT

host = '127.0.0.1'
port = 8889

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='server.crt')
context.load_cert_chain(certfile='client.crt', keyfile='client.key')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname='server')
conn.connect((host, port))


n = input("MSG: ")
conn.send(n.encode())
