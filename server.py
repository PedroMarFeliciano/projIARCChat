import select, socket, pickle
from datetime import datetime

# Cria socket TCP/IP
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #ao inicio todas as conexões sao bloqueadoras.
    #Com esta função deixam de o ser. setblobcking(0 ou 1)
    server.setblocking(0)
except socket.error:
    print("Erro no socket. ")

server_address = ('localhost', 50057)
print ('starting up on: %s, port: %s' %server_address)

#Para evitar que outra aplicação corra no porto 50055
server.bind(server_address)
server.listen(5)

#Lista de todos os sockets dos quais vamos ler a informação.
inputs = [server]

# outputs e' a lista de sockets nos quais vamos escrever
outputs = []

#Dicionario{chave - nome de utilizador; valor - socket}
#O valor de cada chave é um tuplo com 2 elementos:
usersip = {}

#Dicionário que armazena a lista de bloqueios por utilizador
blocks = {}

# dicionário que cuja chave é o nome do grupo e o valor é uma lista de sockets, de
# todos que participam da conversa
groups = {}


def addToHistory(msg):
    instant = datetime.now()
    date = "["+str(instant.day)+"/"+str(instant.month)+"/"+str(instant.year)+"-"
    date = date +str(instant.hour)+":"+str(instant.minute)+":"+str(instant.second)+"]"

    with open("chat_history.txt", "a") as ch:

        ch.write(date + " " + msg + "\n")
        ch.close()

# envia, para o utilizador que fez a requisição, a lista de usuarios online
def user_list(requester_socket):
    lst = ""
    for nick in usersip.keys():
        lst = lst + nick + "\n" + " " * 22
    lst = "Utilizadores ligados: " + lst
    requester_socket.send(lst.encode())


#Marco adiciona o user ao dicionario users e ao dicionarios bloqueios
#no dicionarios bloqueios o valor é inicializado com uma lista vazia.
#no início ainda não há utilizadores bloqueados
#retorna True para nicks únicos e False quando já existe um utlizador
#utlizando esse apelido.
def val_nick(nick, addr):
    if (nick not in usersip.keys()):
        usersip.setdefault(nick,addr)
        blocks.setdefault(nick,[])
        print("novo user adicionado\t" + nick)
        return True
    return False

# função para verificar se o nome do grupo existe no dicionario que guarda todos
# os nomes de grupos
def notExistingGroup(group_name):
    if group_name not in groups.keys():
        return True
    return False

# verifica se um usuário está ou não em um determinado grupo
def userNotInGroup(user, group_name):
    if user not in groups[group_name]:
        return True
    return False

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for sock in readable:
        # se socket for o servidor significa que existe um novo pedido de conexao
        if sock is server:
            connection, client_adress = sock.accept()
            print("Nova conexao de ", client_adress)
            
            # garante que os apelidos sejam únicos
            unique = False

            while not unique:
                new_user_nickname = connection.recv(4096).decode()

                # guarda o apelido do novo usuario e também seu endereço IP e porto
                unique = val_nick(new_user_nickname, connection)

                connection.send(pickle.dumps(unique))
            
            inputs.append(connection)
            outputs.append(connection)

        # caso não seja o socket do servidor, é uma mensagem
        else:
            data = sock.recv(1024).decode() #decodifica a mensagem enviada
            #Só é necessário fazer se o servidor precisar de tratar a mensagem.
            messages.append(data)

            if data:
                #Marco Cria uma lista com a mensagem recebida
                #nick[0],comando[1], mensagem ou user a bloquear
                proc_data = data.split(" ")
                nick = proc_data[0]
                cmd = proc_data[1]

                #Mensagem de grupo
                if(cmd == ".grp"):
                    # proc_data[2] é o comando ou nome do grupo

                    # caso o utilizador queira criar um grupo
                    if proc_data[2] == 'crt':
                        # proc_data[3] é o nome do grupo

                        # verifica se esse nome está em uso
                        if notExistingGroup(proc_data[3]):
                            # cria uma nova entrada no dicionario de grupos
                            groups[proc_data[3]] = [usersip[nick]]

                            sock.send('Grupo criado com sucesso.'.encode())
                            print("Grupo", proc_data[3], "criado.")
                        else:
                            sock.send('Esse nome já está em uso. Tente outro.'.encode())

                    # adiciona um usuário
                    elif proc_data[2] == 'add':
                        # proc_data[3] é o nome do grupo e proc_data[4] o apelido do
                        # usuário que tentam adicionar ao grupo

                        # verifica se o grupo existe
                        if notExistingGroup(proc_data[3]):
                            sock.send("Esse grupo ainda não foi criado.".encode())
                        # verifica se o usuario que tenta adicionar um integrante ao
                        # grupo faz parte desse grupo
                        elif userNotInGroup(usersip[nick], proc_data[3]):
                            sock.send('Você não faz parte desse grupo.'.encode())
                        # adiciona um novo usuário ao grupo
                        else:
                            msg = "Você foi adicionado ao grupo " + proc_data[3]
                            usersip[proc_data[4]].send(msg.encode())
                            groups[proc_data[3]].append(usersip[proc_data[4]])
                    
                    # remove um usuário
                    elif proc_data[2] == 'rem':
                        # proc_data[3] é o nome do grupo e proc_data[4] o apelido do
                        # usuário que tentam remover do grupo

                        # verifica se o grupo existe
                        if notExistingGroup(proc_data[3]):
                            sock.send("Esse grupo ainda não foi criado.".encode())
                        # verifica se o usuario que tenta remover um integrante do
                        # grupo faz parte desse grupo
                        elif usersip[nick] != groups[proc_data[3]].index(0):
                            sock.send('Você não é o administrador desse grupo.'.encode())
                        # remove o socket do usuário da lista de sockets daquele grupo
                        else:
                            msg = "Você foi removido do grupo " + proc_data[3]
                            usersip[proc_data[4]].send(msg.encode())
                            groups[proc_data[3]].remove(usersip[proc_data[4]])

                    # lista os grupos do qual o utilizador faz parte
                    elif proc_data[2] == 'lst':
                        sock.send("Grupos do quais faz parte: ".encode())
                        for k in groups.keys():
                            if sock in groups[k]:
                                msg = k + '\n                           '
                                sock.send(msg.encode())
                        else:
                            sock.send("você não faz parte de grupo algum.\n".encode())
                                
                    # envia mensagem para o grupo
                    elif proc_data[2] in groups.keys():
                        # verifica se o usuario que tenta remover um integrante do
                        # grupo faz parte desse grupo
                        if userNotInGroup(usersip[nick], proc_data[2]):
                            sock.send('Você não faz parte desse grupo.'.encode())
                        # envia a mensagem
                        else:
                            msg = nick+' disse no grupo '+proc_data[2]+': '+" ".join(proc_data[2::])
                            addToHistory(msg)

                            for u in groups[proc_data[2]]:
                                u.send(msg.encode())

                # lista os utilizadores online
                elif cmd == ".lst":
                    user_list(sock)

                # bloqueia ou desbloqueia um usuario
                elif cmd == ".block":
                    # se o usuario já estiver na lista de bloqueio ele é removido
                    # caso contrário é adicionado
                    if proc_data[2] in blocks[nick]:
                        blocks[nick].remove(proc_data[2])
                    else:
                        blocks[nick].append(proc_data[2])

                #Mensagem privada
                elif(cmd == ".priv"):
                    #Valida se o recetor existe
                    if proc_data[2] not in usersip.keys():
                        sock.send("Utilizador inexistente.".encode())
                    
                    # teste se o usuario que enviou a mensagem está na lista de bloqueio
                    # do destinatário
                    elif nick not in blocks[proc_data[2]]:
                        # envia a mensagem para o utilizador destino
                        msg = " ".join(proc_data[3::])
                        addToHistory(nick+" disse privadamente para "+proc_data[2]+' '+msg)
                        msg = nick + " diz privadamente: " + msg
                        usersip[proc_data[2]].send(msg.encode())
                    
                    else:
                        sock.send("Você foi bloqueado por esse utilizador.".encode())

                else:

                    msg = nick + " diz para todos: " + " ".join(proc_data[1::])
                    addToHistory(msg)
                    for s in outputs:
                        s.send(msg.encode())

            else:
                inputs.remove(sock)
                outputs.remove(sock)

                # remove utilizador dos grupos dos quais faz parte
                for k in groups.keys():
                    if sock in groups[k]:
                        groups[k].remove(sock)

                # remove o utilizador da lista de usuários ativos
                for k in usersip.keys():
                    if usersip[k] == sock:
                        del usersip[k]
                        break

                sock.close()

