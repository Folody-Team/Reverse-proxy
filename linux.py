import socketserver
import socket
import traceback
from multiprocessing.pool import ThreadPool as Pool

class MyTCPSocketHandler(socketserver.ThreadingMixIn, socketserver.StreamRequestHandler):

    def handle(self):
        # server connect to client
        endpoints = ("192.168.1.14", 3333)
        print("Got connection from", self.client_address[0])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(endpoints)
                s.sendall(self.request.recv(1024))
                pool = Pool()
                rev = pool.apply_async(recv_data_send ,args=(s,self.request))
                sen = pool.apply_async(recv_data_send, args=(self.request, s))
                while not (rev.ready() or sen.ready()):
                    pass
                pool.close()
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
            if check_alive(req) or check_alive(sock):
                return
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
