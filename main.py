import asyncio
import ssl
import threading
from time import sleep

import event_parser
import event_types

from online_handler import UserStore

host = "localhost"
port = 8889

server_cert = 'server.crt'
server_key = 'server.key'

online_store = UserStore()


def periodic_online_task():
    while True:
        online_req = event_types.OnlineRequest()
        online_req.new_online_users_list(list(online_store.user_writer_map))
        req_string = online_req.convert_to_string()
        for wr in online_store.user_writer_map.values():
            wr.write(req_string.encode())
        sleep(1)


def get_ssl_context():
    context = ssl.create_default_context()
    context.verify_mode = ssl.CERT_OPTIONAL
    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    return context


# named in honor of its predecessor
# https://github.com/akulinski/ChatRoomServer
# it writes the DATA (not only messages) to all clients
# its name confusing as we all are
async def pass_massage(message):
    for w in online_store.user_writer_map.values():
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


async def handle_connection(reader, writer):
    addr = writer.get_extra_info('peername')
    print(str(addr) + " connected")

    while True:
        try:
            data = await get_data_from_client(reader)
            event = event_parser.EventParser().parse_string_to_event(data)
        except (IndexError, ValueError) as e:
            removed_username = online_store.remove_by_writer(writer)
            if not removed_username == None:
                print("removing: "+ str(removed_username))
                writer.close()
                message = event_types.MessageRequest("SERVER", removed_username+ " disconnected")
                await pass_massage(message.convert_to_string())
            break

        if event.event_type == event_types.MESSAGE_REQUEST:
            print(data)
            await pass_massage(data)

        elif event.event_type == event_types.LOGIN_REQUEST:
            print(data)

            code = ''

            if not online_store.check_if_online(event.login):
                code = event_types.CODE_ACCEPT
            else:
                code = event_types.CODE_REJECT

            login_response = event_types.LoginResponse(code)

            if login_response.code == event_types.CODE_ACCEPT:
                online_store.add_new_user(event.login, writer)

            await send_data_to_client(writer, login_response.convert_to_string())

        else:
            await send_data_to_client(writer, "mordo ja nie wiem")

        await writer.drain()


async def run_server():
    server = await asyncio.start_server(
        handle_connection,
        host,
        port,
        ssl=get_ssl_context()
    )

    addr = server.sockets[0].getsockname()
    print("Serving on " + str(addr))

    async with server:
        await server.serve_forever()


threading.Thread(target=periodic_online_task).start()
asyncio.run(run_server())
