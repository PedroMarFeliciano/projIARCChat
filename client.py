import socket, sys, select, pickle, os

def beep():
	os.system("aplay -q beep.wav")

def clear():
	os.system("clear")

def helpMenu():
	print("Comandos úteis:")
	print("Acções disponíveis:")
	print("Mostra menu de ajuda...........: .help")
	print("Listar utilizadores online.....: .lst")
	print("Criar grupo....................: .grp crt <nome do grupo>")
	print("Adiciona utilizador ao grupo...: .grp add <nome do grupo> <nome utilizador>")
	print("Remove utilizador do grupo.....: .grp rem <nome do grupo> <nome utilizador>")
	print("Mensagem de grupo..............: .grp <nome do grupo> <mensagem>")
	print("Lista de grupos que pertence...: .grp lst")
	print("Mensagem privada...............: .priv <nome do utilizador> <mensagem>")
	print("Bloquear/desbloquear utilizador: .block <nome do usuario>")
	print("Limpa o ecrã...................: .clear")
	print("Desativar/ativar alerta sonoro.: .som")
	print("-"*80 + '\n')

server_address = ('localhost', 50057)

server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_connection.connect(server_address)

unique = False

while not unique:
	nickname = input("Digite seu apelido: ")

	#@ Marco Remove espaços de nickname
	nickname = nickname.replace(" ","")

	# envia o nickname para o servidor
	server_connection.send(nickname.encode())

	unique_ser = server_connection.recv(4096)
	unique = pickle.loads(unique_ser)

	if not unique:
		clear()
		print("Apelido em utilização. Escolha outro.")

clear()

print("Bem vindo(a) ao chat,", nickname + '.')
helpMenu()

# lista de sockets a ser ouvida pelo select
sockets = [server_connection, sys.stdin]
sound = True

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
				if sound:
					beep()

		# Marco significa que outro utilizou msg?		
		else:
			inp = input()

			if inp == '.help':
				helpMenu()
			elif inp == '.clear':
				clear()
			elif inp == '.som':
				if sound:
					sound = False
					print("Alerta sonoro desligado.")
				else:
					sound = True
					print("Alerta sonoro ligado.")
			else:
				msg = nickname + " " +  inp
				server_connection.send(msg.encode())