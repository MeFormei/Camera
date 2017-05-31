from server import WebSocketServer
import time
import random
import json


websocket_server = WebSocketServer(port=9000)
websocket_server.start()

while True:
    directions = ['NORTH', 'SOUTH', 'EAST', 'WEST']
    dir_idx = random.randint(0, 3)
    websocket_server.send_message('direction', directions[dir_idx])
    time.sleep(1)
    websocket_server.send_message('position', json.dumps({'x': random.randint(0, 352), 'y': random.randint(0, 240) }))
    time.sleep(1)
