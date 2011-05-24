#!/usr/bin/python
# coding=UTF-8
import socket
import time
import sys
import string
import select
import mc_blocks

# Multiplexer configuration settings
mc_socket = '/home/minecraft/tmp/plexer.sock'
from mc_private import *

class multiplexer_connection:
	outbox = []
	socket = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
	sockfile = ''
	password = ''
	status = { 'connected' : False, 'authenticated' : False }
	buffer = ''
	data = ''
	events = []
	players = []

	def __init__( self, sockfile, port = None, password = None ):
		self.sockfile = sockfile
		self.password = password
		self.port = port
	
	def connect( self ):
		print ( 'Connecting to Minecraft Multiplexer..' )
		try:
			print( '  Opening socket..' )
			self.socket.connect( self.sockfile )
			print( '  Setting non-blocking.' )
			self.socket.setblocking( False )
			self.socket.settimeout( 3 )
		except:
			print( '  Failed to connect\n' + str( sys.exc_info() ) )
			self.status['connected'] = False
			self.socket.close()
			sys.exit( 1 )
		print ( '  Connection established.' )
		self.status['connected'] = True
		self.authenticate()

	def authenticate( self ):
		#	This transaction is pretty well known, which is why it's not looped through select()
		print( 'Authenticating to Multiplexer..' )
		try:
			data = self.socket.recv( 96 )
			if data[0] == '-':
				print( '  Got password request.  Sending password. ')
				self.socket.send( self.password + '\r\n' )
				data = self.socket.recv( 4096 )
				if data[0] == '+':
					self.status['authenticated'] = True
					print( '  Multiplexer authenticated.' )
				else:
					print( '  Multiplexer authentication failed.' )
		except:
			print( '  Failed to authenticate\n' + str( sys.exc_info() ) )
			self.status['connected'] = False
			self.socket.close()
			sys.exit( 1 )

	def disconnect( self ):
		print ('Closing connection to Multiplexer..' )
		self.socket.send( '' )
		self.status['connected'] = False
		self.status['authenticated'] = False
		self.socket.close()

	def cmd( self, text ):
		print( 'Sending command to Multiplexer: ' + text )
		self.socket.send( text + '\r\n' )

	def say( self, text ):
		line = ''
		surline = '§8[^]§a '
		writeline = False
		#	Find "words" that are too long, and redact them.
		wordlist = [ word if len( word ) < 85 else word[:4] + '§8[...]§a' + word[-4:] for word in text.split() ]

		#	Now to make it MC-size bites.
		for word in wordlist:
			if len( line ) + len( word ) > 100:
				if writeline:
					self.cmd( 'say ' + line )
					line = surline
					writeline = False
				else:
					#	We should never be here, but cry if we are.
					print( 'MCM> Something went wrong in mp_class.say() with line:' )
					print( 'MCM> ' + text )
			else:
				line = line + word + ' '
				writeline = True
		if writeline:
			self.cmd( 'say ' + line )


	def cycle( self ):
		self.data = self.socket.recv( 128 )
		self.buffer += self.data
		if not self.events:
			lines = self.buffer.split( '\n' )	
			while( len(lines) >= 2 ):
				self.events.append( lines[0] )
				lines = lines [1:]
			self.buffer = lines[0]
		if self.events:
			for e in self.events:
				eparts = e.split()
				if len(eparts) > 3:
					if eparts[3][0] == '<' or eparts[3] == '[CONSOLE]':
						# Looks like someone's talking.
						talker  = eparts[3][1:-1]	# strip the leading and trailing brackets
						chatter = ' '.join(eparts[4:])
						if chatter:


							if len(chatter) > 2 and chatter[:2] == '??':
								# Someone's asking what something is.
							
								query = ''.join( chatter[2:] )
								print("?? query: " + query)
								answer = mc_blocks.lookup(query)
								print("?? answer: " + str(answer))
								self.cmd('say [*] ' + query + ' is ' + str(answer) + '.')

#							elif len(chatter) > 4 and chatter[:4].upper() in ( '?map', '?gps' ):
#								coords = ''.join( chatter[4:] ).split( ' ' )
#								if len( coords ) == 2: 
#									self.cmd( 'say [*] Not fully implemented (2 arg)' )
#									self.cmd( 'say [*] Args: ' + ' '.join( coords ) )
#								elif len( coords ) == 3:		
#									self.cmd( 'say [*] Not fully implemented (3 arg)' )
#									self.cmd( 'say [*] Args: ' + ' '.join( coords ) )
#								else:
#									self.cmd( 'say [*] Usage: ?map X [Y] Z' )

							elif chatter[0] == "?":
								# It's a command for the bot!
								botcmds = ['?WHO', '?PLAYERS', '?LOAD', '?WTF', '?TIME', '?MAP', '?MUMBLE']
								keyword = chatter.split(' ')[0][1:].upper()
								if keyword == "HELP":
									self.cmd('say Available commands:')
									self.cmd('say [*] ' + ' '.join(botcmds))
								elif keyword in ['WHO', 'W', 'PLAYERS']:
									self.cmd('list')
								elif keyword in ['MUMBLE']:
									self.cmd( 'say [*] Mumble server at wold.its.lsu.edu' )
									self.cmd( 'say [*] Contact DG, Thvortex, or Sunfall for PW.')
								elif keyword == 'LOAD':
									u = open('/proc/loadavg', 'r')
									l = u.readline().split()[0]
									u.close()
									self.cmd('say [*] Current system load is ' + l)
								elif keyword in ('MAP', 'GPS'):
									self.cmd('say [*] Not yet implemented, ' + talker)
								elif keyword.upper in ['WTF', 'TIME']:
									self.cmd('say [*] Not yet implemented, ' + talker)
							elif chatter[0] == "/":
								#	Someone issued a command to the server. Do nothing.
								pass
							elif len(chatter) > 5 and ( chatter.upper()[-5:] == '> IRC' or chatter.upper()[-4:] == '>IRC' ):
								# Someone is talking to IRC, old-school.
								chatter = chatter[:-3]
								self.outbox.append( '14<9' + talker + '14> 11' + chatter )
								self.cmd( 'tell ' + talker + ' [*] That notation is no longer needed.' )
							else:
								if talker != "CONSOLE":
									#	chatter = chatter[:-3]
									self.outbox.append( '14<9' + talker + '14> 11' + chatter )

					elif  eparts[3][0] == "*":
						#	Someone is acting
						#	self.outbox.append (' action stub ' ) 
                                                talker  = eparts[4]       # strip the leading and trailing brackets
						chatter = ' '.join(eparts[5:])
						self.outbox.append( ' 11* 9' + talker + ' 11' + chatter )

					elif ' '.join(eparts[3:5]) == 'Connected players:':
						# Someone asked who's playing.  Public knowledge, so relay it to all.
						self.cmd('say [*] Currently playing: ' + ' '.join(eparts[5:]))
						self.players = eparts[5:]
			self.events = []


#	End of class definition

def testloop():
	# And now, let's connect to the Minecraft Multiplexer
	print( 'Attempting to connect to Minecraft Multiplexer' )
	mc_conn = multiplexer_connection( '/home/minecraft/tmp/plexer.sock', None, 'aardvark' )
	mc_conn.connect()

	sock_list = [ mc_conn.socket ]

	try:
		while ( mc_conn.status['connected'] and mc_conn.status['authenticated'] ):
			#	Check for any pending messages from the sockets
			( sock_out, sock_in, sock_exception ) = select.select( sock_list, [], [] )
			for s in sock_out:
				if s == mc_conn.socket:
					mc_conn.cycle()
	#			if s == irc_conn.socket:
	#				irc_conn.cycle()

			#	Check for any pending messages for the sockets.
			if( len( mc_conn.outbox ) > 0 ):
				#	We have messages for IRC
				for message in mc_conn.outbox:
					#	Display what we've got and where it's going
					print( 'MC  > ' + message )
					# irc_conn.relay( message )
				mc_conn.outbox = []
			time.sleep(0.1)

	except KeyboardInterrupt:
		print( 'SIGINT caught from keyboard.' )
		mc_conn.disconnect()
	except IndexError:
		pass
	#except Exception, e:
	#	print 'Got exception: ' + e.__str__()
	#	mc_conn.disconnect()

#	testloop()
