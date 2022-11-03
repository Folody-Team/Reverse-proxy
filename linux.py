import socketserver
import socket
import traceback
import os
import time
from multiprocessing.pool import ThreadPool as Pool

timeout_sec = 60

class MyTCPSocketHandler(socketserver.ThreadingMixIn, socketserver.StreamRequestHandler):
    _timeout = None

    def check_timeout(self):
        if self._timeout is None:
            return False
        else:
            return (time.monotonic() >= self._timeout)

    def recv_data_send(self, req, sock):
        try:
            while True:
                if check_alive(req) or check_alive(sock):
                    return
                try:
                    data = req.recv(1024)
                    if len(data) != 0:
                        sock.send(data)
                        if timeout_sec:
                            self._timeout = time.monotonic() + timeout_sec
                    else:
                        break
                except:
                    break
        except:
            return

    def handle(self):
        self.requestid = os.urandom(16).hex()
        # server connect to client
        endpoints = ("192.168.1.14", 3333)
        print("Got Request ID: %s" % self.requestid)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(endpoints)
                s.sendall(self.request.recv(1024))
                if timeout_sec:
                    self._timeout = time.monotonic() + timeout_sec
                pool = Pool()
                rev = pool.apply_async(self.recv_data_send ,args=(s,self.request))
                sen = pool.apply_async(self.recv_data_send, args=(self.request, s))
                while not (rev.ready() or sen.ready() or self.check_timeout()):
                    pass
                pool.terminate()
                s.close()
                print("Request %s Closed" % self.requestid)
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


if __name__ == "__main__":
    # Create the server at port 80
    PORT = 80
    server = socketserver.ThreadingTCPServer(("0.0.0.0", PORT), MyTCPSocketHandler)

    print("Serving at {}".format(PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        server.shutdown()
        server.server_close()
        print("Server closed")
        exit(0)
