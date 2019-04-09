import socket, time, sys
import json
import threading
from queue import Queue


#-----------------------------------------------------------------------------------------------------------------------------
# Три потока: Один ждет новых подключений(1); Другой отправляет команды(2); Последний ждет команд от мобильного приложения(3);
#-----------------------------------------------------------------------------------------------------------------------------

NUMBER_OF_THREADS = 3
JOB_NUMBER = [1,2,3]
queue = Queue() 
all_connections = []
all_adress = []
all_mobileapps = []
all_mobadress = []


#---------------------------------------------------------------------------------------------------------
#----------------
# Создание сокета
#----------------
#---------------------------------------------------------------------------------------------------------

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
	del all_mobileapps[:]
	del all_mobadress[:]

	# Ожидание новых подключений
	while True:
		try:
			conn, address = s.accept()
			s.setblocking(1) # Предотвращение timeout
			id_app = 'mobileapp' # Строчка-идентификатор от mob app

			#-------------------------------------------------------------------------
			# Пытаемся определить мобильное приложение. 
			# Если вместе с подключением мы получаем строчку "Я мобильное приложение",
			# то кладем айпи conn в отдельный массив all_mobileapps.
			# Если мы получили пустую строчку, то к серверу подключился гаджет-клиент
			#-------------------------------------------------------------------------

			# Возможная проблема: Сервер не будет захватывать данные, отправленные приложением-клиентом

			chunk = conn.recv(1024)
			if chunk in id_app:
				all_mobileapps.append(conn)
				all_mobadress.append(address)
			else:
				all_connections.append(conn)
				all_adress.append(address)

			print("Connection has been established: " + address[0])

		except:
			print("Error accepting connections")
			break


#---------------------------------------------------------------------------------------------------------
#-------------------------------------------------
# Функции второго (2) потока:
# 1) Просмотр всех подключенных клиентов к серверу
# 2) Выбор клиента
# 3) Отправка команды клиенту
#-------------------------------------------------
#---------------------------------------------------------------------------------------------------------


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

		results_clinet = str(i) + "  " + str(all_adress[i][0]) + "  " + str(all_adress[i][1]) + '/n'

	for i,conn in enumerate(all_mobileapps):
		# Смотрим подключено ли клиенты мобильного приложения
		try:
			conn.send(str.encode(' '))
			conn.recv(201480)

		except:
			del all_mobileapps[i]
			del all_mobadress[i]
			continue

		results_apps = str(i) + "  " + str(all_mobadress[i][0]) + "  " + str(all_mobileapps[i][1]) + '/n'

	print("---- Clients ----" + '\n' + results_clinet)
	print("---- Apps ----" + '\n' + results_apps)


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


#---------------------------------------------------------------------------------------------------------
#------------------------------------------
# Получение данных от мобильного приложения
#------------------------------------------
#---------------------------------------------------------------------------------------------------------


def recive_json_msg():

	# Получаем json. Пытаемся Прочитать его и записать в фал вид 1, 2, 3
	# эти цифры соответсвуют номеру мобильно приложения, с которого был сделан запрос.

	while True:
		for i,conn in enumerate(all_mobileapps):
			fname = os.path.basename(i)
			with open(fname, 'wd') as json_file:
				
				while True:
					tmp = conn.recv(1024)
					if not tmp:
						break
					json_file.write(tmp)

				json_file.close()
				
				if os.stat(fname).st_size != 0:
					parse_json(fname)
				# Нужно отчищать файлы каждого приложения


#---------------------------------------------------------------------------------------------
# Парсер json файла. Определяет команду для сервера, тип устройства, его ip и команду для него
#---------------------------------------------------------------------------------------------


def parse_json(fname):
	# Открываем json для чтения
	with open(fname, "r") as read_file:
		data_dump = json.load(read_file)

	serv_cmd = data_dump['serv_cmd'] # Команда для сервера
	type_apl = data_dump['type'] # Тип устройства
	apl_ip = data_dump['apl_ip'] # ip выбранного устройства
	apl_cmd = data_dump['apl_cmd'] # Команда для выбранного устройства

	if serv_cmd == 'select':
		json_cmd = serv_cmd + ' ' + apl_ip # Строчка типа select 192.168.0.100
		conn = get_target(json_cmd)  # Выдает conn клиента
		send_json_target_commands(conn, apl_cmd) # Отправляет команды на выбранный девайс для выплнения

	read_file.close()

#----------------------------------------
# Отправка команд на выбранное устройство
#----------------------------------------


def send_json_target_commands(conn, apl_cmd):
	try:
		cmd = apl_cmd
		# Отправляем команды и ждем ответа от клиентов
		if len(str.encode(cmd)) > 0:
			conn.send(str.encode(cmd))
			client_response = str(conn.recv(20480), 'utf-8')
			print(client_response, end='')

	except:
		print('Error sending commands')


#---------------------------------------------------------------------------------------------------------
#-----------------
# Создание потоков
#-----------------
#---------------------------------------------------------------------------------------------------------


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

		if x == 3:
			recive_json_msg()

		queue.task_done()


def create_jobs():

	for x in JOB_NUMBER:
		queue.put(x)

	queue.join()


create_workers()
create_jobs()
