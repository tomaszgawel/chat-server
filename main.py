import asyncio
import ssl
import event_parser
import event_types

host = "localhost"
port = 8889

writers = []
logins = []


server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'


def get_ssl_context():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED

    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    context.load_verify_locations(cafile=client_certs)

    return context


# named in honor of its predecessor
# https://github.com/akulinski/ChatRoomServer
# it writes the DATA (not only messages) to all clients
# its name confusing as we all are
async def pass_massage(message):
    for w in writers:
        w.write(message.encode())


async def send_data_to_client(client_writer, message):
    client_writer.write(message.encode())


async def get_data_from_client(reader):
    read_size = 1024
    data = await reader.read(1024)
    length = event_parser.get_full_length(data.decode())

    while read_size < length:
        data += await reader.read(1024)
        read_size += 1024

    return data.decode()


def check_if_login_exist(login):
    if not login in logins:
        return event_types.CODE_ACCEPT
    else:
        return event_types.CODE_REJECT


async def handle_connection(reader, writer):
    addr = writer.get_extra_info('peername')
    print(str(addr) + " connected")

    while True:
        try:
            data = await get_data_from_client(reader)
            event = event_parser.EventParser().parse_string_to_event(data)
        except IndexError:
            await writer.drain()
            continue

        if event.event_type == event_types.MESSAGE_REQUEST:
            print(data)
            await pass_massage(data)

        elif event.event_type == event_types.LOGIN_REQUEST:
            print(data)
            login_response = event_types.LoginResponse(check_if_login_exist(event.login))

            if login_response.code == event_types.CODE_ACCEPT:
                writers.append(writer)
                logins.append(event.login)

            await send_data_to_client(writer, login_response.convert_to_string())

        else:
            await send_data_to_client(writer, "mordo ja nie wiem")

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
