import json
import threading

import tornado.ioloop
from tornado import websocket


class WebSocket(websocket.WebSocketHandler):

    clients = []

    def open(self, *args, **kwargs):
        print("Websocket opened")
        WebSocket.clients.append(self)

    def on_message(self, message):
        print("message: {}".format(message))

    def send_message(self, message):
        self.write_message(message)

    def check_origin(self, origin):
        return True

    def on_close(self):
        print("Websocket closed")
        WebSocket.clients.remove(self)


class WebSocketServer(threading.Thread):

    def __init__(self, port=9000):
        super(WebSocketServer, self).__init__()
        self.daemon = True
        self.port = port
        self.application = tornado.web.Application([(r"/", WebSocket)])

    def send_message(self, topic, data):
        message = {'topic': topic, 'data': data}
        message_json = json.dumps(message)

        for client in WebSocket.clients:
            client.send_message(message_json)
            print('(ws) {} - {}'.format(topic, data))

    def run(self):
        self.application.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()
