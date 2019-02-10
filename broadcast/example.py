import broadcast
from threading import Thread

port = 1337

broadcast.broadcastInit(port)

announsingThread = Thread(target=broadcast.broadcastIpAnnounsing, args=(10, port,))
sniffingThread = Thread(target=broadcast.broadcastListener, args=(port,))

announsingThread.start()
sniffingThread.start()