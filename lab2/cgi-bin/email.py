import sys

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

body = "[ SMTP ]\r\n"
## START

body += "{ from: " + param.get("from", "<unknown>") + " }\r\n"
body += "{ to: " + param.get("to", "<unknown>") + " }\r\n"
body += "{ body: " + param.get("body", "<unknown>") + " }\r\n"
body += "{ server: " + param.get("server", "<unknown>") + " }\r\n"
body += "{ auth: " + param.get("auth", "<unknown>") + " }\r\n"
body += "{ username: " + param.get("username", "<unknown>") + " }\r\n"
body += "{ password: " + param.get("password", "<unknown>") + " }\r\n"

## END
body += "[ done ]\r\n"
bodysize = sys.getsizeof(body)

sys.stdout.write("Content-Type: text/plain\r\n")
sys.stdout.write("Content-Length: " + str(bodysize) + "\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(body)
