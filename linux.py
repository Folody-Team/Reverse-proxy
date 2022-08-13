import socketserver
import socket
import traceback
from threading import Thread


class MyTCPSocketHandler(socketserver.ThreadingMixIn, socketserver.StreamRequestHandler):

    def handle(self):
        # server connect to client
        endpoints = ("192.168.1.14", 8080)
        print("Got connection from", self.client_address[0])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(endpoints)
                s.sendall(self.request.recv(1024))
                d = Thread(target=recv_data_send ,args=(s,self.request))
                d1 = Thread(target=recv_data_send ,args=(self.request, s))
                d.start()
                d1.start()
                isclose = False
                while not isclose:
                    data = check_alive(s)
                    if data:
                        isclose = True
                    data2 = check_alive(self.request)
                    if data2:
                        isclose = True
                d.join(timeout=0)
                d1.join(timeout=0)
                s.close()
            self.request.close()
        except Exception as e:
            traceback.print_exc()
            self.request.close()
            return

def check_alive(s):
    try:
        data = s.recv(1024, socket.MSG_PEEK | socket.MSG_DONTWAIT)
        isclose = False
    except BlockingIOError:
        isclose = False
    except Exception as e:
        isclose = True
    return isclose

# get data from client and send to server and reveive from server and send to client
def recv_data_send(req, sock):
    try:
        while True:
            try:
                data = req.recv(1024)
                if len(data) != 0:
                    sock.send(data)
                else:
                    break
            except:
                break
    except:
        return

if __name__ == "__main__":
    # Create the server at port 80
    PORT = 2912
    server = socketserver.ThreadingTCPServer(("0.0.0.0", PORT), MyTCPSocketHandler)

    print("Serving at {}".format(PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        server.shutdown_request()
        server.server_close()
        print("Server closed")
        exit(0)
