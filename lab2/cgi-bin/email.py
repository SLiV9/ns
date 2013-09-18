import sys
import socket
import urllib

## Read the enviroment variables.
env = {}

args = sys.stdin.read()
while (args.find("\r\n") >= 0):
	line, args = args.split("\r\n", 1)
	if (line.find("=") >= 0):
		vname, vval = line.split("=", 1)
		env[vname] = vval
	#end if find =
#end while

## Read the parameters.
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
		## unquote to replace %40 -> @ and %0A -> \n, etc.
		## also replace + with sp
		param[pname] = urllib.unquote(pval).replace("+", " ")
	#end if find =
#end while

## Get a full line of code from the buffer, that is until a CRLF (or LF).
def getline(s, leftover):
	msg = leftover
	endx = msg.find("\n")
	while (endx < 0):
		msg += s.recv(8)
		endx = msg.find("\n")
	leftover = msg[endx+1:]
	msg = msg[0:endx]

	last = True
	spx = msg.find(" ")
	hpx = msg.find("-")

	if (hpx >= 0 and (spx < 0 or spx > hpx)):
		status, text = msg.split("-", 1)
		text = text.rstrip()
		last = False
	elif (spx >= 0):
		status, text = msg.split(" ", 1)
		text = text.rstrip()
	else:
		status = msg
		text = ""
	#end if find sp

	return status, last, text, leftover

def send_cmd(s, cmd):
	msg = "" + cmd + "\r\n"
	s.send(msg)
	return "> " + msg

def print_reply(status, last, text):
	if (last):
		return "< " + status + "  " + text + "\r\n"
	else:
		return "< " + status + "- " + text + "\r\n"

def check_ok(status, okcodes, failcodes):
	if (status in okcodes):
		return ""
	elif (status in failcodes):
		return "\t(Execution failed. Quiting...)\r\n"
	else:
		return "\t(Unexpected status. Quiting...)\r\n"

## Run the SMTP protocol.
def run_smtp(s, param):
	log = ""
	leftover = ""

	## Wait for server to send greeting.
	last = False
	while (not last):
		status, last, text, leftover = getline(s, leftover)
		log += print_reply(status, last, text)
	rep = check_ok(status, {"220"}, {"554"})
	if (len(rep) > 0):
		log += rep
		return log

	## Send extended HELLO.
	fqdn = socket.getfqdn()
	log += send_cmd(s, "EHLO " + fqdn)

	last = False
	while (not last):
		status, last, text, leftover = getline(s, leftover)
		log += print_reply(status, last, text)
	rep = check_ok(status, {"250"}, {"504", "550"})
	if (len(rep) > 0):
		log += rep
		return log

	"""
	## If Authentication is enabled, send STARTTLS command.
	auth = param.get("auth", "none")
	if (auth == "tls"):
		log += send_cmd(s, "STARTTLS ")

		last = False
		while (not last):
			status, last, text, leftover = getline(s, leftover)
			log += print_reply(status, last, text)
		rep = check_ok(status, {"220"}, {"501", "454"})
		if (len(rep) > 0):
			log += rep
			return log
		
		return log
	#end if tls
	"""

	## Send MAIL (FROM) command.
	frm = param.get("from", "unknown")
	log += send_cmd(s, "MAIL FROM:<" + frm + ">")

	last = False
	while (not last):
		status, last, text, leftover = getline(s, leftover)
		log += print_reply(status, last, text)
	rep = check_ok(status, {"250"}, {"552", "451", "452", "550", "553", "503"})
	if (len(rep) > 0):
		log += rep
		return log

	## Send RECIPIENT (TO) command.
	to = param.get("to", "unknown")
	log += send_cmd(s, "RCPT TO:<" + to + ">")

	last = False
	while (not last):
		status, last, text, leftover = getline(s, leftover)
		log += print_reply(status, last, text)
	rep = check_ok(status, {"250", "251"}, {"550", "551", "552", "553", "450", "451", "452", "503", "550"})
	if (len(rep) > 0):
		log += rep
		return log

	## Send DATA command.
	log += send_cmd(s, "DATA")

	last = False
	while (not last):
		status, last, text, leftover = getline(s, leftover)
		log += print_reply(status, last, text)
	rep = check_ok(status, {"354"}, {"451", "554", "503"})
	if (len(rep) > 0):
		log += rep
		return log

	## Determine the actual data.
	frmln = "From: <" + frm + ">"
	toln = "To: <" + to + ">"
	subjln = "Subject: " + param.get("subject", "untitled") + ""

	bdy = param.get("body", "")
	if (bdy.find("\n") >= 0):
		lns = bdy.split("\n")
	else:
		lns = []
	#end if find \n

	data = [frmln, toln, subjln, ""]
	for ln in lns:
		data.append(ln.rstrip())
	#end for

	## Send the actual data.
	for d in data:
		log += send_cmd(s, d)
	#end while

	## Send the 'end of data' command.
	log += send_cmd(s, ".")

	last = False
	while (not last):
		status, last, text, leftover = getline(s, leftover)
		log += print_reply(status, last, text)
	rep = check_ok(status, {"250"}, {"552", "554", "451", "452"})
	if (len(rep) > 0):
		log += rep
		return log

	## Send the QUIT command.
	log += send_cmd(s, "QUIT")

	last = False
	while (not last):
		status, last, text, leftover = getline(s, leftover)
		log += print_reply(status, last, text)
	rep = check_ok(status, {"221"}, {})
	if (len(rep) > 0):
		log += rep
		return log
	
	## Transaction succesful.
	return log

body = "[ SMTP ]\r\n\r\n"
## START

if (len(param.get("server", "")) == 0):
	body += "Fatal error: no server specified.\r\n"
else:
	server = param["server"]
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((server, 25))
	leftover = ""

	log = run_smtp(s, param)
	body += log

	s.close()
#end if serveraddr empty

## END
body += "\r\n[ done ]\r\n"
bodysize = sys.getsizeof(body)

sys.stdout.write("Content-Type: text/plain\r\n")
sys.stdout.write("Content-Length: " + str(bodysize) + "\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(body)
