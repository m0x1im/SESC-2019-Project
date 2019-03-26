import socket
import sys


# Создание сокета
def create_socket():
	try:
		global host
		global port
		global s
		host = ''
		port = 11111 # Можно любой другой удобный порт
		s = socket.socket()
		
	except socket.error as msg:
		print("Socket creation error" + str(msg))


# Привязка и прослушивание сокета
def bind_socket():
	try:
		global host
		global port
		global s

		s.bind((host, port))
		s.listen(5)

	except socket.error as msg:
		print("Socket Binding error" + str(msg) + "/n" + 'Retrying...')
		bind_socket()



# Установка связи с локальным сервером
def socket_accept():
	conn, address = s.accept() 
	send_commands(conn)
	conn.close()


# Отправка команд на локльный сервер
def send_commands(conn):
	while True:
		cmd = input()
		if cmd == 'quit':
			conn.close()
			s.close()
			sys.exit()
		if len(str.encode(cmd)) > 0:
			conn.send(str.encode(cmd))
			client_response = str(conn.recv(1024), 'utf-8')
			print(client_response, end='')


def main():
	create_socket()
	bind_socket()
	socket_accept()

main()