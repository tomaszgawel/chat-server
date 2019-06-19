import asyncio
import ssl
import event_parser
import event_types

host = "localhost"
port = 8889

writers = []
client_dict = {}  # "ip": "login"


server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'  # might not be needed


def get_ssl_context():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED

    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    context.load_verify_locations(cafile=client_certs)

    return context


# named in honor of its predecessor
# https://github.com/akulinski/ChatRoomServer
async def pass_massage(message):
    for w in writers:
        w.write(message.encode())


async def pass_massage_to_client(writer, message):
    writer.write(message.encode())


async def get_data_from_clinet(reader):
    read_size = 1024
    data = await reader.read(1024)

    while read_size < event_parser.get_full_length(data.decode()):
        data += await reader.read(1024)
        read_size += 1024

    return data.decode()


async def handle_connection(reader, writer):
    writers.append(writer)
    addr = writer.get_extra_info('peername')
    print(str(addr) + " connected")

    while True:
        data = await get_data_from_clinet(reader)
        event = event_parser.EventParser().parse_string_to_event(data)

        if event.event_type == event_types.MESSAGE_REQUEST:
            await pass_massage(data)
        elif event.event_type == event_types.LOGIN_REQUEST:
            await pass_massage_to_client(writer, data)
        else:
            await pass_massage("mordo ja nie wiem")

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
