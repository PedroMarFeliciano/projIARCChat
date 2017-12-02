import socket, sys, select, pickle, os

def clear():
	os.system("clear")

server_address = ('localhost', 50051)

server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_connection.connect(server_address)

unique = False

while  not unique:
	nickname = input("Digite seu apelido: ")
	# envia o nickname para o servidor
	server_connection.send(nickname.encode())

	unique_ser = server_connection.recv(4096)
	unique = pickle.loads(unique_ser)

	if not unique:
		clear()
		print("Apelido em utilização. Escolha outro.")

clear()
print("Bem vindo(a) ao chat,", nickname + '.')

user_list_ser = server_connection.recv(4096)
user_list = pickle.loads(user_list_ser)

print("Existem", len(user_list), "utilizadores online.\nUtilizadores:")

for user in user_list:
	print(user)

print("\nPara enviar uma mensagem privada digite .<nomeDoUtilizador> <mensagem>")

#lista de sockets ouvida pelo select
sockets = [server_connection, sys.stdin]

while True:
	read_sockets, write_sockets, error_sockets = select.select(sockets, [], [])

	for s in read_sockets:
		# Mensagem recebida
		if s is server_connection:
			clear()
			serialized_msg = s.recv(4096)

			msgs = pickle.loads(serialized_msg)

			if not msgs:
				print("Problema com o servidor.")
				sys.exit(1)
			else:

				for m in msgs:
					print(m)

		else:
			msg = nickname + " diz: " + input()
			server_connection.send(msg.encode())
