import sys
from subprocess import PIPE, Popen, STDOUT
from threading  import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.stdout.close()

p = Popen(['powershell'], stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1, close_fds=ON_POSIX)
q = Queue()
t = Thread(target=enqueue_output, args=(p.stdout, q))
t.daemon = True # thread dies with the program
t.start()

# ... do other things here

# read line without blocking
# print p.stdout.readline()
while ( 1 ):
	try:  
		# line = q.get_nowait() # or q.get(timeout=.1)
		line = q.get(timeout=.2)
	except Empty:
	    answer = raw_input('> ')
	    p.stdin.write(answer + '\n')
	else: # got line
	    # ... do something with line
	    print(line),