#!/usr/bin/python

import socket
import multiplexlib
import time
import sys
import string
import select

# Define our IRC Class
class IRC:
	server = 'irc.example.com'
	port = 6667
	nick = 'NickName'
	status = { 'connected' : False, 'registered' : False }
	data = ''
	buffer = ''
	events = []
	socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	print_next_event = True

	def __init__( self ):
		self.connect( )

	def connect( self ):
		print ('Connecting to IRC..')
		try:
			print( 'Opening socket..' )
			self.socket.connect( ( self.server, self.port ) )
			self.status['connected'] = True
			print( 'IRC Socket connected.' )
		except:
			print( 'Failed to connect\n' + sys.exc_info() )
			self.status['connected'] = False

	def register( self ):
		if self.status['registered'] == False:
			self.send( 'NICK ' + self.nick )
			self.send( 'USER ' + self.nick + ' ' + self.nick + ' ' + self.nick + 
					' :Testing IRC Connector' )
			self.status['registered'] = True

	def cycle( self ):
		if len( self.events ) == 0:
			try:
				self.data = self.socket.recv( 4096 )
			except socket.error:
				self.status['connected'] = False
				return( str( sys.exc_info() ) )
			if self.data == '':
				self.status['connected'] = False
				return( 'Connection reset by peer' )
			if not self.status['registered']:
				self.register()
			self.parse_data()
		next_ev = self.events.pop( 0 )
		if self.print_next_event:
			print( 'IRC > ' + next_ev )
		return( self.event_handler( next_ev ) )

	def event_handler( self, event ):
		self.print_next_event = True
		self.data = event.rstrip( '\r' )
		sdata = self.data.split( ' ' )

		if sdata[0] == 'PING':
			print( 'Playing Ping-Pong.' )
			self.send( 'PONG ' + ' '.join( sdata[1:] ) )
		elif sdata[1] == '433':		#	Nick in use
			self.nick += '_'
			self.register()
		elif sdata[1] in ('375', '372', '376'):		#	MOTD
			self.print_next_event = False
		return( self.data )

	def parse_data( self ):
		self.data = self.buffer + self.data
		self.events = self.data.split( '\n' )
		self.buffer = self.events.pop()

	def send( self, text ):
		self.socket.send( text + '\r\n' )
		print ( 'IRC < ' + text )
		

# So, let's connect to IRC!
print( 'Attempting to connect to IRC' )
conn = IRC()

# And now, let's connect to the Minecraft Multiplexer
# TODO: Exception handling for Plexer not being there to connect to
# TODO: Make this a class like IRC.
print( 'Attempting to connect to Minecraft Multiplexer' )
ml = multiplexlib.MinecraftRemote(socket.AF_UNIX, '/pather/to/your/plexer.sock', 9001, 'password')
ml.connect()
print( 'Multiplexer connected.' )

# We don't want to look for args as this isn't an instant client. What we do want to do
# is connect to IRC.

# Vestigal code from the generic plexer client.

#if len(sys.argv) > 1:
#    ml.send_command('%s' % string.join(sys.argv[1:], " ").decode('utf-8'))
#    (sout, _, _) = select.select([ml.client_socket], [], [], 1)
#
#    if sout == []:
#        exit()
#    else:
#        print ml.receive()
#        ml.disconnect()
#else:

try:
	while conn.status['connected']:

	# See if there is anything pending _from_ IRC
		conn.cycle()

	# see if there is anything pending _from_ Minecraft
		pass
	#mc.cycle

	# See if there is anything pending _for_ IRC
		pass

	# See if there is anything pending _for_ Minecraft
		pass

		

#	More vestigal code from the generic client.

#        (sout, sin, sexc) = select.select([sys.stdin, ml.client_socket],
#                                          [],
#                                          [])
   
#        if sout != []:
#            for i in sout:
#                if i == sys.stdin:
#                    line = sys.stdin.readline()
   
#                    if line == '':
#                        ml.disconnect()
#                        exit()
#                    else:
#                        pass
#                       ml.send_command(line.rstrip().decode('utf-8'))
#                else:
#                    line = ml.receive()
   
#                    if line == '':
#                        ml.disconnect()
#                        exit()
#                    else:
#                        print line


#	Exit on a ^C or other exception
except KeyboardInterrupt:
    print 'Exiting.'
except Exception, e:
    print 'Got exception: ' + e.__str__()

