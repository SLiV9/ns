## Netwerken en Systeembeveiliging Lab 3 - Chat Room (Client)
## NAME: Sander in 't Veld
## STUDENT ID: 10277935
import socket
import select
from gui import MainWindow

def loop(port, cert):
	"""
	GUI loop.
	port: port to connect to.
	cert: public certificate (bonus task)
	"""

	host = "127.0.1.1"

	# Connect to the server.
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	isconnected = True

	# The following code explains how to use the GUI.
	w = MainWindow()
	w.writeln("[ Connected to server. ]")

	# update() returns false when the user quits or presses escape.
	while (w.update()):

		# If the user entered a line getline() returns a string.
		line = w.getline()
		if line:
			# If the user did not specify a command, assume /say.
			if (isconnected):
				if (line.find("/") == 0):
					s.send(line + "\n")
				else:
					s.send("/say " + line + "\n")
			else:
				w.writeln("[ Not connected. ]")
			#end if isconnected
		#end if line

		# if s is readable, read
		if (isconnected):
			rrdy, wrdy, err = select.select([s], [], [], 0)
			for r in rrdy:
				msg = r.recv(256)
				msg = msg.rstrip()
				if (len(msg) > 0):
					w.writeln(msg)
				else:
					w.writeln("[ Connection to server lost. ]")
					isconnected = False
			#end for r
		#end if isconnected

	#end while update

	# Close connection.
	s.close()
	return

## Command line parser.
if __name__ == '__main__':
	import sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--port', help='port to connect to', default=12345, type=int)
	p.add_argument('--cert', help='server public cert', default='')
	args = p.parse_args(sys.argv[1:])
	loop(args.port, args.cert)

