from server import WebSocketServer
import time
import random


websocket_server = WebSocketServer(port=9000)
websocket_server.start()

while True:
    directions = ['NORTH', 'SOUTH', 'EAST', 'WEST']
    dir_idx = random.randint(0, 3)
    websocket_server.send_message('direction', directions[dir_idx])
    time.sleep(1)
    websocket_server.send_message('position', (random.randint(0, 352), random.randint(0, 240)))
    time.sleep(1)
