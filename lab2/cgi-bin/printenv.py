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

body = """<h1>Enviroment Variables</h1>"""

if (env):
	for vname, vval in env.iteritems():
		body += "<p><strong>" + vname + " =</strong> " + vval + "</p>"
else:
	body += "<p><em>None.</em></p>"
#end if env notempty

bodysize = sys.getsizeof(body)

sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("Content-Length: " + str(bodysize) + "\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(body)
