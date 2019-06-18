import asyncio
import ssl

host = "localhost"
port = 8889

writers = []
client_dict = {} #"ip": "login"

server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt' # might not be needed


def get_ssl_context():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    context.load_verify_locations(cafile=client_certs)
    return context

# named in honor of its predecessor
# https://github.com/akulinski/ChatRoomServer
def pass_massage(message):
    for w in writers:
        # to be changed for protocol handling
        w.write(message.encode())


async def handle_connection(reader, writer):
    writers.append(writer)
    addr = writer.get_extra_info('peername')
    print(str(addr) + " connected")
    while True:
        data = await reader.read(100)
        pass_massage(data.decode())
        await writer.drain()


async def run_server():
    server = await asyncio.start_server(
         handle_connection,
         host,
         port,
         #ssl=get_ssl_context() # disabled for testing only
    )
    addr = server.sockets[0].getsockname()
    print("Serving on " + str(addr))
    async with server:
        await server.serve_forever()

asyncio.run(run_server())
