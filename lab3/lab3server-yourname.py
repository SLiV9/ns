## Netwerken en Systeembeveiliging Lab 3 - Chat Room (Server)
## NAME:
## STUDENT ID:

def serve(port, cert, key):
	"""
	Chat server entry point.
	port: The port to listen on.
	cert: public certificate (bonus task)
	key: private key (bonus task)
	"""
	pass


## Command line parser.
if __name__ == '__main__':
	import sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--port', help='port to listen on', default=12345, type=int)
	p.add_argument('--cert', help='server public cert', default='')
	p.add_argument('--key', help='server private key', default='')
	args = p.parse_args(sys.argv[1:])
	serve(args.port, args.cert, args.key)

