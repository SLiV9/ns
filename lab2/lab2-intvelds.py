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

			if (uri.find("/cgibin/") == 0 or uri.find("/cgi-bin/") == 0):
				## CGIBIN RESPONSE
				uri = uri.replace("/cgi-bin/", "/cgibin/", 1)
				fname = cgibin + uri[7:]
				cgicmd = ["python", fname]
				print "The client wants to run: " + fname

				if (os.path.isfile(fname)):
					bfrname = ".temp"
					with open (bfrname, 'w') as f:
						subprocess.call(cgicmd, stdin=None, stdout=f)

					with open(bfrname, 'rb') as f:
						c.send(f.read())
					c.send("\r\n")
				else:
					send_statuspage(c, 404)
				#end if file exists

				## END CGIBIN RESPONSE
			else:
				## NORMAL RESPONSE
				fname = public_html + uri
				if (uri[-1] == '/'):
					fname += "index.html"
				print "The client requested: " + fname

				if (os.path.isfile(fname)):
					c.send("HTTP/1.1 200 OK.\r\n")
					c.send("Connection: close\r\n")
					filesize = os.path.getsize(fname)
					c.send("Content-Length: " + str(filesize) + "\r\n")
					filetype, fileenc = mimetypes.guess_type(fname)
					c.send("Content-Type: " + str(filetype) + "\r\n")
					c.send("\r\n")
					with open(fname, 'rb') as f:
						c.send(f.read())
					c.send("\r\n")
				else:
					send_statuspage(c, 404)
				#end if file exists

				## END NORMAL RESPONSE
			#end if cgibin

		else:
			send_statuspage(c, 501)
		#end if method

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

# Send a default status page, such as a 404.
def send_statuspage(c, status):
	if (status == 404):
		name = "File Not Found"
		desc = "The file you requested does not exist or could not be found."
	elif (status == 501):
		name = "Not Implemented"
		desc = "The method you requested does not exist or has not been \
		implemented."
	else:
		name = "Error"
		desc = "An error has occured."
	#end if status

	page = "<h1>" + str(status) + " " + name + """</h1>
	<p>""" + desc + "</p>"

	c.send("HTTP/1.1 " + str(status) + " " + name + ".\r\n")
	c.send("Connection: close\r\n")
	c.send("Content-Type: text/html\r\n")
	c.send("Connect-Length: " + str(sys.getsizeof(page)) + "\r\n")
	c.send("\r\n")
	c.send(page)
	c.send("\r\n")
	return

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
