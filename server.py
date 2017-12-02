import select, socket, pickle
from datetime import datetime


def writeToFile(chatMessages):
    instant = datetime.now()
    date = "["+str(instant.day)+"/"+str(instant.month)+"/"+str(instant.year)+"-"
    date = date +str(instant.hour)+":"+str(instant.minute)+":"+str(instant.second)+"]"

    with open("chat_history.txt", "a") as f:

        f.write(date + " - " + chatMessages + "\n")
        f.close()

# Cria socket TCP/IP
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
except socket.error:
    print("Erro no socket.")

server_address = ('localhost', 50051)
print ('starting up on: %s, port: %s' %server_address)


server.bind(server_address)
server.listen(5)
# inputs e' a lista de sockets dos quais vamos ler
inputs = [server]

# outputs e' a lista de sockets nos quais vamos escrever
outputs = []

# fila de mensagens para enviar
messages = []

# dicionario que lista o apelido dos usuarios e seus sockets
users = {}

# lista com o nome dos usuarios
users_list = []

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for sock in readable:
        # se socket for o servidor significa que existe um novo pedido de conexao
        if sock is server:
            connection, client_adress = sock.accept()
            print("Nova conexao de ", client_adress)

            unique = False

            while not unique:
                new_user_nickname = connection.recv(4096).decode()

                if new_user_nickname not in users:
                    unique = True

                connection.send(pickle.dumps(unique))

            # guarda o apelido do novo usuario e também seu socket
            users[new_user_nickname] = connection
            users_list.append(new_user_nickname)

            for u in users_list:
                print(u)
            connection.setblocking(0)
            # envia a lista de usuarios conectados para o cliente
            users_list_ser = pickle.dumps(users_list)
            print("aqui: ", users_list_ser)
            connection.send(users_list_ser)
            

            inputs.append(connection)
            outputs.append(connection)
            
        # caso nao seja o socket do servidor, e uma mensagem
        else:
            data = sock.recv(4096).decode()

            if data:
                print("Recebi a mensagem '%s' de '%s'" % (data, sock.getpeername()))
                
                messages.append(data)

                writeToFile(data)

                serialized_msgs = pickle.dumps(messages)

                for s in outputs:
                    s.send(serialized_msgs)