import socket
import time
import sys
import string
import select

# Define our IRC Class
class IRC:
	server = ''
	port = 6667
	nick = ''
	channel = ''
	status = { 'connected' : False, 'registered' : False, 'joined' : False}
	chanlist = []
	data = ''
	buffer = ''
	events = []
	socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	print_next_event = True
	outbox = ''

	def __init__( self, server, port, nick, channel ):
		#TODO: add error-checking and sanity checks
		self.server = server
		self.port = port
		self.nick = nick
		self.channel = channel
		self.connect( )

	def connect( self ):
		print ('Connecting to IRC..')
		try:
			print( 'Opening socket..' )
			self.socket.connect( ( self.server, self.port ) )
			self.status['connected'] = True
			print( 'IRC Socket connected.' )
		except:
			print( 'Failed to connect\n' + str( sys.exc_info() ) )
			self.status['connected'] = False
			sys.exit( 1 )

	def disconnect( self, reason ):
		print( 'Terminating IRC connection..' )
		self.send( 'QUIT :' + reason )

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
		self.outbox = ''
		self.print_next_event = True
		self.data = event.rstrip( '\r' )
		sdata = self.data.split( ' ' )

		if sdata[0] == 'PING':
			self.send( 'PONG ' + ' '.join( sdata[1:] ) )
		elif sdata[1] == '433':				#	Nick in use
			self.nick += '_'
			self.register()
		elif sdata[1] in ('375', '372', '376'):		#	MOTD
			self.print_next_event = False
		elif ( ( sdata[1] == 'PRIVMSG' ) and ( ( sdata[2] == self.channel ) or ( sdata[2] == self.nick ) ) ):
			print( 'IRC > Message for me!')		#	XXX
			#	The message is to us or the channel we're in.  Let's see if it's for Minecraft.
			#	The message should end with "> MC".
			if sdata[-2:] == ['>', 'MC']:
				self.outbox = ' '.join( sdata[3:-2] )		#	If they just said "> MC", this will be a null string.
				self.outbox = self.outbox.lstrip( ':' )		#	That pesky IRC protocol colon.
			#	Now, handle some special commands:
			if sdata[3].lstrip( ':' ) in ('?server', '?minecraft' ):
				self.say( 'The minecraft server can be found at ghoti.dyndns.org.  For more information, say "#link 673".' )

		#		0						1	2		3
		#	IRC > :DopeGhoti!~ghoti@ip98-177-177-13.ph.ph.cox.net PRIVMSG ###linkulator :Ignore this message
		#	IRC > :DopeGhoti!~ghoti@ip98-177-177-13.ph.ph.cox.net PRIVMSG ###linkulator :but this should go > MC

		return( self.data )

	def say( self, text ):
		self.send( 'PRIVMSG ' + self.channel + ' :' + text )

	def parse_data( self ):
		self.data = self.buffer + self.data
		self.events = self.data.split( '\n' )
		self.buffer = self.events.pop()

	def send( self, text ):
		self.socket.send( text + '\r\n' )
		print ( 'IRC < ' + text )

	def join( self ):
		print( 'Attempting to join ' + self.channel )
		self.send( 'JOIN ' + self.channel )
		self.status['joined'] = True
		
