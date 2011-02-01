#!/usr/bin/python
import socket
import time
import sys
import string
import select
import mc_blocks

# Multiplexer configuration settings
mc_socket = '/home/minecraft/tmp/plexer.sock'
mc_password = 'aardvark'

class multiplexer_connection:
	outbox = []
	socket = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
	sockfile = ''
	password = ''
	status = { 'connected' : False, 'authenticated' : False }
	buffer = ''
	data = ''
	events = []

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

	def cycle( self ):
		self.data = self.socket.recv( 8192 )
		self.buffer += self.data
		if( len(self.events) < 1 ):
			lines = self.buffer.split( '\n' )	
			while( len(lines) >= 2 ):
				self.events.append( lines[0] )
				lines = lines [1:]
			self.buffer = lines[0]
		if( len( self.events) > 0 ):
			for e in self.events:
				eparts = e.split( ' ' )
				if( len( eparts ) > 3 ) and ( eparts[3] != '') :
					if ( eparts[3][0] == '<' ) or (eparts[3] == '[CONSOLE]' ):
						#	Looks like someone's talking
						talker  = eparts[3][1:-1]		# strip the leading and trailing < and >
						chatter = ' '.join(eparts[4:] ).strip()
						if( e.strip().upper()[-5:] == '> IRC' ):
							#	Someone is talking to IRC
							#print( eparts )
							chatter = chatter[:-5]
							self.outbox.append( '<' + talker + '> ' + chatter )
						if( chatter[0] == '?' ):
							#	It's a command for the bot!
							botcmds = [ '?WHO', '?PLAYERS', '?LOAD', '?WTF', '?TIME' ]
							keyword = chatter.split(' ')[0][1:]
							if( keyword.upper() == 'HELP' ):
								self.cmd( 'say Available commands:' )
								self.cmd( 'say [*] ' + ' '.join( botcmds ) )
							elif( keyword.upper() in [ 'WHO', 'W', 'PLAYERS' ] ):
								self.cmd( 'list' )
							elif( keyword.upper() == 'LOAD' ):
								u = open( '/proc/loadavg', 'r' )
								l = u.readline().split()[0]
								u.close()
								self.cmd( 'say [*] Current system load is ' + l )
							elif( keyword.upper() in [ 'WTF', 'TIME' ] ):
								self.cmd( 'say [*] Not yet implemented, ' + talker )
						if( (chatter[0:2] == '??' ) and ( chatter.strip() != '??') ):
							#	Someone's asking what something is.
							
							query = ''.join( chatter[2:] ).strip()
							print ("?? query: " + query )
							answer = mc_blocks.lookup( query )
							print ("?? answer: " + str(answer) )
							self.cmd( 'say [*] ' + query + ' is ' + str(answer) + '.' )
					if( ' '.join(eparts[3:5]).strip() == 'Connected players:' ):
						#	Someone asked who's playing.  Public knowledge, so relay it to all.
						self.cmd( 'say [*] Currently playing: ' + ' '.join(eparts[5:]))
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
