import sys
import socket

# Read the enviroment variables.
env = {}

args = sys.stdin.read()
while (args.find("\r\n") >= 0):
	line, args = args.split("\r\n", 1)
	if (line.find("=") >= 0):
		vname, vval = line.split("=", 1)
		env[vname] = vval
	#end if find =
#end while

# Read the parameters.
querystring = env["QUERY_STRING"]
param = {}

while (len(querystring) > 0):
	if (querystring.find("&") >= 0):
		segm, querystring = querystring.split("&", 1)
	else:
		segm = querystring
		querystring = ""
	#end if find &
	
	if (segm.find("=") >= 0):
		pname, pval = segm.split("=", 1)
		param[pname] = pval
	#end if find =
#end while

# Get a full line of code from the buffer, that is until a CRLF (or LF).
def getline(s, leftover):
	msg = leftover
	endx = msg.find("\n")
	while (endx < 0):
		msg += s.recv(8)
		endx = msg.find("\n")
	leftover = msg[endx+1:]
	msg = msg[0:endx]

	if (msg.find(" ") >= 0):
		status, text = msg.split(" ", 1)
	else:
		status = msg
		text = ""
	#end if find sp

	return status, text, leftover

body = "[ SMTP ]\r\n"
## START

body += "{ from: " + param.get("from", "<unknown>") + " }\r\n"
body += "{ to: " + param.get("to", "<unknown>") + " }\r\n"
body += "{ body: " + param.get("body", "<unknown>") + " }\r\n"
body += "{ server: " + param.get("server", "<unknown>") + " }\r\n"
body += "{ auth: " + param.get("auth", "<unknown>") + " }\r\n"
body += "{ username: " + param.get("username", "<unknown>") + " }\r\n"
body += "{ password: " + param.get("password", "<unknown>") + " }\r\n"

if (len(param.get("server", "")) == 0):
	body += "Fatal error: no server specified.\r\n"
else:
	server = param["server"]
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((server, 25))

	leftover = ""
	while True:
		status, text, leftover = getline(s, leftover)
		body += "< " + status + ": " + text + "<\r\n"		
		break
	#end while

	s.close()
#end if serveraddr empty

## END
body += "[ done ]\r\n"
bodysize = sys.getsizeof(body)

sys.stdout.write("Content-Type: text/plain\r\n")
sys.stdout.write("Content-Length: " + str(bodysize) + "\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(body)
