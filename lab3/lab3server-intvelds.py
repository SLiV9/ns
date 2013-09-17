## Netwerken en Systeembeveiliging Lab 3 - Chat Room (Server)
## NAME: Sander in 't Veld
## STUDENT ID: 10277935
import socket
import select

def serve(port, cert, key):
	"""
	Chat server entry point.
	port: The port to listen on.
	cert: public certificate (bonus task)
	key: private key (bonus task)
	"""
	print "[ server ]\n"

	## Get socket.
	s = socket.socket()
	host = socket.gethostname()
	s.bind((host, port))
	## Set SO_REUSEADDR to prevent "socket already in use" errors during testing.
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	print "Listening as {h} on port {p}...".format(h=host, p=port)

	connected = [s]
	s.listen(1)
	while True:
		rrdy, wrdy, err = select.select(connected, [], [])
		for c in rrdy:
			pass
		#end for c
	#end while true

	print "\n[ done ]"
	return

## Command line parser.
if __name__ == '__main__':
	import sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--port', help='port to listen on', default=12345, type=int)
	p.add_argument('--cert', help='server public cert', default='')
	p.add_argument('--key', help='server private key', default='')
	args = p.parse_args(sys.argv[1:])
	serve(args.port, args.cert, args.key)

