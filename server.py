import gevent

from gevent.server import StreamServer

STATE = {'clients': {}, 'name2address': {}}

def register(state, name):
    # Kolla så namnet inte redan finns.
    global_state = state["global_state"]
    if name in global_state['name2address']:
        return "Error: Name already registered!\n"

    # Registrera namnet
    state['name'] = name
    global_state['name2address'][name] = state['address']

    #sätt namnet på klienten
    global_state['clients'][state['address']]['name'] = name

    # Skicka tillbaka hälsning
    return "Hej {}\n".format(name)


def deregister(state, name):
    """
    Remove name, from name2address state

    local function, no return value
    """
    global_state = state["global_state"]
    if name in global_state['name2address']:
        global_state['name2address'].pop(name)


def status(state, nothing):
    return "status: {}\n".format(state)


def shout(state, msg):
    clients = state['global_state']['clients']
    msg = "{} is shouting: {}\n".format(state['name'], msg)
    for address, client in clients.items():
        if address == state['address']:
            continue  # don't send to yourself
        try:
            client['socket'].send(msg.encode('utf-8'))
        except Exception as e:
            print("got exception sending msg: {}".format(e))

    return "all sent\n"


def tell(state, command):
    try:
        name, msg = command.split(' ', maxsplit=1)
    except ValueError:
        return "Error: bad command format\n"
    global_state = state["global_state"]
    if name not in global_state['name2address']:
        return "Error: Name {} isn't registered!\n".format(name)

    address = global_state['name2address'][name]
    if address not in global_state['clients']:
        deregister(state, name)
        return "Error: {}:s client {} has vanished\n".format(name, address)
    socket = global_state['clients'][address]['socket']
    socket.send("{} says: {}\n".format(state['name'], msg).encode('utf-8'))
    return "sent msg to {}\n".format(name)


def quit(state, nothing):
    deregister(state, state['name'])
    return "bye\n"


COMMANDS = {
    "IAM": register,
    "QUIT": quit,
    "STATUS": status,
    "SHOUT": shout,
    "TELL": tell,
}


def _handle(state):
    socket = state['socket']
    socket.send("hej {}\n".format(state['name']).encode("utf-8"))
    while(True):

        data = socket.recv(1024)
        print("raw:")
        print(data)
        
        data = data.decode("utf-8").strip()
        if not data:
            print(data)
            break

        command, *command_data = data.split(" ", maxsplit=1)
        print("command data: {}".format(command_data))
        if command_data:
            command_data = command_data[0]

        if command in COMMANDS:
            result = COMMANDS[command](state, command_data)
            socket.send(result.encode("utf-8"))
        else:
            msg = "I don't understand, are you trying to hack me?\n"
            socket.send(msg.encode("utf-8"))

        if command == 'QUIT':
            break


def handle(socket, address):
    name = '{}:{}'.format(*address)
    STATE['clients'][address] = {'socket': socket, 'name': name}
    state = {
            "global_state": STATE,
            "socket": socket,
            "address": address,
            "name": name}
    print('new connection {}!'.format(address))

    try:
        _handle(state)
    except Exception as e:
        print("got exception when handle client {}: {}".format(name, e))

    STATE['clients'].pop(address)


def main():
    server = StreamServer(('0.0.0.0', 1234), handle)
    server.serve_forever()

if __name__ == '__main__':
    main()


