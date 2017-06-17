import socket 
from sys import argv

def main():    	
    port = int(argv[1])
    path = argv[2]
    
    f = None
    try:
        f = open(path)
    except:
        print 'error occurs when open file'
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = ('127.0.0.1', port)
        sock.bind(server_addr)
        sock.listen(1)
        while True:
            connection, client_addr = sock.accept()
            data = connection.recv(1024)
            print 'get data %s' % data
            msg = check(f, data)
            connection.send(str(msg))
        sock.close()
    except socket.error, exc:
        print 'server error %s' % exc
    finally:
        sock.close()

def check(base, data):
    line = base.read()
    return 1 if data in line else 0

if __name__ == '__main__':
    if len(argv) != 3:
        print 'wrong argument'
        print 'python smsengineTCP.py [port number] [file path]'
    else:
        main()
