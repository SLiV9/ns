## Netwerken en Systeembeveiliging Lab 3 - Chat Room (Server)
## NAME: Sander in 't Veld
## STUDENT ID: 10277935
import socket
import select

alice = ["ALICE", "BOB", "CAROL", "DAVE", "EVE", "FRANK", "IVAN", "TRUDY", "OSCAR", "PEGGY", "VICTOR", "WALTER", "MERLIN"]
connected = []
usernamelist = {}

def standardname(r):
	inx = (id(r) / 3) % 13
	last = (id(r) / 39) % 4096
	name = alice[inx] + hex(last)[2:]
	return name

def username(r):
	return usernamelist.get(id(r), standardname(r))

def set_username(r, name):
	usernamelist[id(r)] = name
	return

def finduser(name):
	for r in connected:
		if (username(r) == name):
			return r
	return None

def listofusers():
	lou = ""
	first = True
	for r in connected:
		if (not first):
			lou += ", "
		lou += username(r)
		first = False
	#end for
	lou += "."
	return lou

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
		elif (cmd == "whisper"):
			if (txt.find(" ") > 0):
				other, txt = txt.split(" ", 1)
				if (finduser(other)):
					respond(finduser(other), "(" + username(r) + ": " + txt + ")")
					respond(r, "(" + username(r) + " to " + other + ": " + txt + ")")
					print "Client '" + username(r) + "' said: '" + txt + "'"
				else:
					respond(r, "% Failure: unknown user '" + other + "'.")
					print "Client '" + username(r) + "' tried: '" + txt + "'; failed."
			else:
				respond(r, "% Failure: invalid syntax. Correct syntax: "
				"'/whisper <user> <message>'.")
				print "Client '" + username(r) + "' tried: '" + txt + "'; failed."
		elif (cmd == "list"):
			respond(r, "% Connected users: " + listofusers())
			print "Client '" + username(r) + "' asked for a list of users."
		elif (cmd == "nick"):
			if (txt.isalnum()):
				newname = txt
				if (not finduser(newname)):
					oldname = username(r)
					set_username(r, newname)
					broadcast("~~ " + oldname + " changed nick to " + newname + ".")
					print "Client '" + oldname + "' changed nick to '" \
					+ txt + "'."
				else:
					respond(r, "% Failure: name '" + newname + "' already taken.")
					print "Client '" + username(r) + "' tried to change nick to '" \
					+ newname + "'; failed."
			else:
				respond(r, "% Failure: invalid syntax. Correct syntax: "
				"'/nick <name>', where <name> alphanumeric.")
				print "Client '" + username(r) + "' tried to empty nick; failed."
		else:
			respond(r, "% Failure: unknown command '" + cmd + "'.")
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
	print "Listening as " + str(host) + " on port " + str(port) + "..."

	s.listen(1)
	while True:

		potred = [s]
		potred.extend(connected)
		rrdy, wrdy, err = select.select(potred, [], [])
		for r in rrdy:
			if (r == s):
				c, addr = s.accept()
				broadcast("++ " + username(c) + " connected.")
				print "Client '" + username(c) + "' at " + str(addr) + " connected."
				connected.append(c)
			else:
				msg = r.recv(256)
				if (len(msg) > 0):
					# msg is an actual message from a client; handle it
					handle_msg(r, msg)
				else:
					connected.remove(r)
					broadcast("-- " + username(r) + " disconnected.")
					print "Client '" + username(r) + "' disconnected."
				#end if empty msg
			#end if r=s
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

