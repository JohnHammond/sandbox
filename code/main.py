#!/usr/bin/env python

import os
import platform
import subprocess
import threading
import sys
import time
# This 'Queue' object keeps the input and output of Powershell buffered.
try:
	from Queue import Queue, Empty
except ImportError:
	from queue import Queue, Empty  # this is the syntax for Python 3...

# We need to know if we are on a POSIX system in order to handle closing
# file descriptors with the subporocess module.
ON_POSIX = 'posix' in sys.builtin_module_names

class Powershell:

	def __init__( self ):

		# This may change depending on the operating system, be wary...
		self.command = "powershell"


		self.process = subprocess.Popen( [ self.command ], 
										 # We have to handle every FD...
										 stdout    = subprocess.PIPE,
										 stdin     = subprocess.PIPE,
										 # Stderr can redirect to  stdout
										 stderr    = subprocess.STDOUT,
										 bufsize   = 1,
										 close_fds = ON_POSIX
										)
		self.queue  = Queue()
		self.thread = threading.Thread( target = self.queue_output,
										args   = ( self.process.stdout,
												   self.queue
												 ) )
		# The thread dies with the program.
		self.thread.daemon = True 

		# All set up... now run PowerShell!
		self.thread.start()

		# receive the  banner so we can process each command henceforth...
		self.receive()


	def queue_output( self, output_fd, queue ): 
		# Iterate through every line in the output and add it to the queue
		for line in iter(output_fd.readline, b''):
			queue.put(line)
		output_fd.stdout.close()


	def get_output( self ):
		'''
		The queue keeps track of output line by line. This function will get 
		only one line.
		'''
		try: return self.queue.get(timeout=1)
		except Empty: return ""


	def send_command( self, string ):
		# Just write to the process's standard input with a newline...
		self.process.stdin.write( string + '\n' )

	
	def receive( self ):
		'''
		`receive` will gather all the output in PowerShell as it comes by 
		waiting for the prompt. WARNING: This is not foolproof!
		'''
		self.send_command('')
		all_data = []
		output = self.get_output()
		while (not output.endswith('> \n') ):
			# print output
			all_data.append(output)
			output = self.get_output()
		else:
			return "".join(all_data)


	def check_output( self, command ):
		'''
		`check_output` aims to mimic the subprocess module. it takes just a 
		command then returns the output.
		'''
		self.send_command(command)
		return "\n".join(self.receive().split('\n')[1:-1])

	def run_command( self, command ):
		'''
		This is a duplicate of `check_output` just for convenience sake.
		'''
		return self.check_output(command)


	def import_powercli( self ):
		return self.run_command( \
			'Get-Module -ListAvailable PowerCLI* | Import-Module' )


	def connect_testing_server( self ):
		'''
		THIS IS A TESTING FUNCTION THAT I INTEND TO REMOVE
		'''
		return self.run_command(\
						'Connect-VIServer 10.1.214.223 '+\
										'-User administrator@vsphere.local '+\
										'-Password S@ndbox2')


if ( __name__ == "__main__" ):
	powershell = Powershell()	
	# print powershell.import_powercli()
	# print powershell.connect_testing_server()
	# print powershell.run_command('(Get-VM).Name')
	print powershell.run_command('whoami')
	# powershell.interactive()
