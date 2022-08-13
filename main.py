import socketserver
import socket
from threading import Thread


class MyTCPSocketHandler(socketserver.ThreadingMixIn,   socketserver.StreamRequestHandler):
    daemon_threads = True
    block_on_close = False

    def handle(self):
        # server connect to client
        endpoints = ("localhost", 8080)
        print("Got connection from", self.client_address[0])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(endpoints)
                s.sendall(self.request.recv(1024))
                s1 = Thread(target=get_send_revest, args=(self.request, s))
                s2 = Thread(target=get_send_revest, args=(s, self.request))
                s1.start()
                s2.start()
                s1.join()
                s2.join()
                s.close()
            self.request.close()
        except Exception as e:
            print(e)
            self.request.close()
            return


# get data from client and send to server and reveive from server and send to client
def get_send_revest(req, sock):
    try:
        while True:
            data = req.recv(1024)
            if len(data) != 0:
                sock.send(data)
            else:
                break
    except:
        pass

if __name__ == "__main__":
    # Create the server at port 80
    PORT = 80
    server = socketserver.ThreadingTCPServer(("0.0.0.0", PORT), MyTCPSocketHandler)

    print("Serving at {}".format(PORT))
    server.serve_forever()