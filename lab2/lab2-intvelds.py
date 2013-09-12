## Netwerken en Systeembeveiliging Lab 2 - HTTP Server
## NAME: Sander in 't Veld
## STUDENT ID: 10277935

import socket

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
	  print "@msg@{s}@msg@".format(s=msg)
	  print "@leftover@{s}@leftover@".format(s=leftover)
	  
	  method, uri, vers = msg.split(" ", 3)
	  if (method == "GET"):
	    if (os.path.isfile(public_html + uri)):
	      c.send("The file exists!")
	    else:
	      c.send("HTTP/1.1 404 File not found.\r\n")
	  else:
	    c.send("HTTP/1.1 501 Method not implemented.\r\n")
	    c.send("\r\n")
	  
	  print "\t[end]"
	  c.close()
	#.
	
	print "[ done ]"
	return
	
def getline(c, leftover):
  """
  Get a full line from the client c, i.e. a string that ends at CLRF.
  """
  msg = leftover
  endx = msg.find("\n")
  while (endx < 0):
    msg += c.recv(8)
    endx = msg.find("\n")
  #.
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
