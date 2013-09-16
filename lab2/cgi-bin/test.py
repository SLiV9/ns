import sys

body = """<h1>Hoofdstuk 12</h1>
<p>Een <em>Algebra</em> <strong>A</strong> op een lichaam <strong>k</strong> is een vectorruimte over <strong>k</strong> met daarop een associatieve, <strong>k</strong>-bilineaire vermenigvuldiging gedefinieerd.</p>"""
bodysize = sys.getsizeof(body)

sys.stdout.write("HTTP/1.1 200 OK\r\n")
sys.stdout.write("Connection: close\r\n")
sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("Content-Length: " + str(bodysize) + "\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(body)
