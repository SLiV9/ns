## Netwerken en Systeembeveiliging Lab 3 - Chat Room (Server)
## NAME: Sander in 't Veld
## STUDENT ID: 10277935
import socket
import select

connected = []
usernamelist = {}

def username(r):
	return usernamelist.get(id(r), str(id(r)))

def broadcast(msg):
	for r in connected:
		r.send(msg)
	return

def respond(r, msg):
	r.send(msg)
	return

def handle_msg(r, msg):
	if (msg.find("/") == 0):
		msg = msg[1:]

		if (msg.find(" ") > 0):
			cmd, txt = msg.split(" ", 1)
		else:
			cmd = msg
			txt = ""
		
		if (cmd == "say"):
			broadcast("" + username(r) + ": " + txt + "")
			print "Client '" + username(r) + "' said: '" + txt + "'"
		else:
			respond(r, "(Failure: unknown command '" + cmd + "'.)")
			print "Client '" + username(r) + "' tried unknown command '" \
			+ cmd + "'; failed."
		#end if cmd

	else:
		print "Client '" + username(r) + "' tried: '" + msg + "'; failed."
	return

# Main method.
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

	s.listen(1)
	while True:

		rrdy, wrdy, err = select.select([s], [], [])
		for s in rrdy:
			c, addr = s.accept()
			print "Client '" + username(c) + "' at " + str(addr) + " connected."
			connected.append(c)
		#end for s

		rrdy, wrdy, err = select.select(connected, [], [])
		for r in rrdy:
			msg = r.recv(256)
			if (len(msg) > 0):
				# msg is an actual message from a client; handle it
				handle_msg(r, msg)
			else:
				connected.remove(r)
				print "Client '" + username(r) + "' disconnected."
			#end if empty msg
		#end for r

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

