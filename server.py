import gevent

from gevent.server import StreamServer

STATE = {}

def register(state, name):
    # Kolla så namnet inte redan finns.
    global_state = state["global_state"]
    if name in global_state:
        return "Error: Name already registered!\n"

    # Registrera namnet
    global_state[name] = {"name": name}

    # Skicka tillbaka hälsning
    return "Hej {}\n".format(name)

commands = {
    "IAM": register
}

def handle(socket, address):
    state = {"global_state": STATE}

    socket.send("hej {}\n".format(address).encode("utf-8"))
    print('new connection!')

    while(True):

        data = socket.recv(1024)
        print("raw:")
        print(data)
        
        data = data.decode("utf-8").strip()
        if not data:
            print(data)
            continue

        command, command_data = data.split(" ", maxsplit=1)

        print(command)
        print(command_data)

        if command in commands:
            result = commands[command](state, command_data)
            socket.send(result.encode("utf-8"))

        print(STATE)


server = StreamServer(('0.0.0.0', 1234), handle)
server.serve_forever()


