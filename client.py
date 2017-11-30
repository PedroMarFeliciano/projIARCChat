import socket, sys, select

server_address = ('localhost', 50055)

nickname = input("Digite seu apelido: ")

server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_connection.connect(server_address)

sockets = [server_connection, sys.stdin]

while True:
	read_sockets, write_sockets, error_sockets = select.select(sockets, [], [])

	for s in read_sockets:
		# Mensagem recebida
		if s is server_connection:
			msg = s.recv(1024).decode()

			if not msg:
				print("Problema com o servidor.")
				sys.exit(1)
			else:
				print(msg)

		else:
			msg = nickname + " diz: " + input()
			server_connection.send(msg.encode())
