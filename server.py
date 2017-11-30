import select, socket, pickle

# Cria socket TCP/IP
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
except socket.error:
    print("Erro no socket. ")

server_address = ('localhost', 50055)
print ('starting up on: %s, port: %s' %server_address)


server.bind(server_address)
server.listen(5)
# inputs e' a lista de sockets dos quais vamos ler
inputs = [server]

# outputs e' a lista de sockets nos quais vamos escrever
outputs = []

# fila de mensagens para enviar
messages = []

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for sock in readable:
        # se socket for o servidor significa que existe um novo pedido de conexao
        if sock is server:
            connection, client_adress = sock.accept()
            print("Nova conexao de ", client_adress)
            connection.setblocking(0)
            inputs.append(connection)
            outputs.append(connection)
            
        # caso nao seja o socket do servidor, e uma mensagem
        else:
            data = sock.recv(1024).decode()
            messages.append(data)

            #serialized_msgs = pickle

            if data:
                #print("Recebi a mensagem '%s' de '%s'" % (data, sock.getpeername()))
                        
                for s in outputs:
                    s.send(data.encode())
            