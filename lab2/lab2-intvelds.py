## Netwerken en Systeembeveiliging Lab 2 - HTTP Server
## NAME: Sander in 't Veld
## STUDENT ID: 10277935

import socket
import mimetypes
import subprocess

def serve(port, public_html, cgibin):
	"""
	The entry point of the HTTP server.
	port: The port to listen on.
	public_html: The directory where all static files are stored.
	cgibin: The directory where all CGI scripts are stored.
	"""
	print "[ start ]"

	## Get socket.
	s = socket.socket()
	host = socket.gethostname()
	s.bind((host, port))
	## Set SO_REUSEADDR to prevent "socket already in use" errors during testing.
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	print "Listening as {h} on port {p}...".format(h=host, p=port)
	
	s.listen(1)
	while True:
		c, addr = s.accept()
		print "A client at {a} connected.".format(a=addr)
		print "\t[start]"

		msg, leftover = getline(c, "")
		method, uri, vers = msg.split(" ", 3)

		if (method == "GET"):

			filefound = False

			if (uri.find("/cgibin/") == 0):
				## CGIBIN RESPONSE
				fname = cgibin + uri[7:]
				cgicmd = ["python", fname]
				print "The client wants to run: " + fname

				if (os.path.isfile(fname)):
					filefound = True

					bfrname = ".temp"
					with open (bfrname, 'w') as f:
						subprocess.call(cgicmd, stdin=None, stdout=f)

					c.send("HTTP/1.1 200 OK.")
					c.send("Connection: close\r\n")
					fileheader = "text"
					body = ""
					with open(bfrname, 'r') as f:
						fileheader = f.readline()
						body = f.read()
					filesize = os.path.getsize(bfrname)
					c.send("Content-Length: " + str(filesize) + "\r\n")
					filetype = fileheader[:fileheader.find(" ")]
					c.send("Content-Type: " + str(filetype) + "\r\n")
					print "@ " + str(filesize) + " @ " + str(filetype)
					c.send("\r\n")
					c.send(body)
					c.send("\r\n")
				#end if file exists

				## END CGIBIN RESPONSE
			else:
				## NORMAL RESPONSE
				fname = public_html + uri
				if (uri[-1] == '/'):
					fname += "index.html"
				print "The client requested: " + fname

				if (os.path.isfile(fname)):
					filefound = True

					c.send("HTTP/1.1 200 OK.")
					c.send("Connection: close\r\n")
					filesize = os.path.getsize(fname)
					c.send("Content-Length: " + str(filesize) + "\r\n")
					filetype, fileenc = mimetypes.guess_type(fname)
					c.send("Content-Type: " + str(filetype) + "\r\n")
					c.send("\r\n")
					with open(fname, 'rb') as f:
						c.send(f.read())
					c.send("\r\n")
				#end if file exists

				## END NORMAL RESPONSE
			#end if cgibin

		else:
			c.send("HTTP/1.1 501 Method not implemented.\r\n")
			c.send("Connection: close\r\n")
			c.send("\r\n")
		#end if method

		if (filefound == False):
			c.send("HTTP/1.1 404 File not found.\r\n")
			c.send("Connection: close\r\n")
			c.send("\r\n")
		#end if file exists

		print "\t[end]"
		c.close()
	#end while True

	print "[ done ]"
	return
	
# Get a full line of code from the buffer, that is until a CRLF (or LF).
def getline(c, leftover):
	msg = leftover
	endx = msg.find("\n")
	while (endx < 0):
		msg += c.recv(8)
		endx = msg.find("\n")
	return msg[0:endx], msg[endx+1:]

## This the entry point of the script.
## Do not change this part.
if __name__ == '__main__':
	import os, sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--port', help='port to bind to', default=8080, type=int)
	p.add_argument('--public_html', help='home directory', default='./public_html')
	p.add_argument('--cgibin', help='cgi-bin directory', default='./cgi-bin')
	args        = p.parse_args(sys.argv[1:])
	public_html = os.path.abspath(args.public_html)
	cgibin      = os.path.abspath(args.cgibin)
	serve(args.port, public_html, cgibin)
