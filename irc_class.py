# coding=UTF-8
import socket
import time
import sys
import string
import select

# Characters recognized as a command prefix in IRC
CMD_PREFIX = [ '?', '!' ]

# Define our IRC Class
class IRC:

	def __init__( self, dispatcher, server, port, nick, channel ):
		self.status = { 'connected' : False, 'registered' : False, 'joined' : False}
		self.join_ok = False
		self.data = ''
		self.buffer = ''
		self.events = []
		self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.print_next_event = True
		self.outbox = []

		#TODO: add error-checking and sanity checks
		self.dispatcher = dispatcher
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
		self.outbox.append( '§7[§c!§7] VoxelHead Offline.' )
		self.send( 'QUIT :' + reason )
		self.socket.close()

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
		temp_outbox = ''
		self.print_next_event = True
		self.data = event.rstrip( '\r' )
		sdata = self.data.split( ' ' )

		if sdata[0] == 'PING':
			self.send( 'PONG ' + ' '.join( sdata[1:] ) )
		elif sdata[1] == '433':				#	Nick in use
			self.nick += '_'
			self.register()
		elif sdata[1] in ('375', '372', '376'):		#	MOTD; clear to /JOIN
			self.join_ok = True
			self.print_next_event = False
		elif ( ( sdata[1] == 'PRIVMSG' ) and ( ( sdata[2] == self.channel ) or ( sdata[2] == self.nick ) ) ):
			#	print( 'IRC > Message for me!')		#	XXX
			#	Raw IRC output:
			#		0						1	2		3
			#	IRC > :DopeGhoti!~ghoti@ip98-177-177-13.ph.ph.cox.net PRIVMSG ###linkulator :Ignore this message
			#	IRC > :DopeGhoti!~ghoti@ip98-177-177-13.ph.ph.cox.net PRIVMSG ###linkulator :but this should go > MC

			#	Figuring out the nick:
			#	      ------------------sdata[0]--------------------- --[1]-- --sdata[2]--- ---[sdata[3]-------
			#	      : Nick    !~user @ Host
			#	IRC > :DopeGhoti!~ghoti@ip98-177-177-13.ph.ph.cox.net PRIVMSG ###linkulator :Ignore this message
			#	therefore,
			#	userhost = sdata[0]
			#	nick = userhost.replace( ':', '', 1 ).split( '!' )[0]

			#	Per above, pick out the nick
			userhost = sdata[0]
			nick = userhost.replace( ':', '', 1 ).split( '!' )[0]

			#	At this point, we know the message is to us or the channel we're in.  
			#	Look for special cases, and forward everything else to the outbox.

			#	In-IRC Bot Commands begin with one and only one prefix character
			keyword = sdata[3].replace( ':', '', 1 ).upper()
			if keyword[0:1] in CMD_PREFIX and not keyword[1:2] in CMD_PREFIX:
				args = sdata[4:]
				if sdata[2] == self.channel:
					self.dispatcher.notify_cmd( self, nick, keyword, args )
				else:
					if keyword[0:1] == '?':
						self.dispatcher.notify_cmd( private_reply( self, nick ), nick, keyword, args )
					else:
						self.send( 'PRIVMSG ' + nick + ' :[!] Only ? commands allowed here. Try using command in channel.' )

			# Chat text in channel. Forward to Minecraft server
			elif sdata[2] == self.channel:
				temp_outbox = ' '.join( sdata[3:] )
				temp_outbox = temp_outbox.replace( ':', '', 1 )		#	Colonectomy
				temp_outbox = '§8[#] §7<§b' + nick + '§7>§a ' + temp_outbox
				self.outbox.append( temp_outbox )
			
			# Chat text in /QUERY or /MSG. Do not forward and complain to the user
			else:
				self.send( 'PRIVMSG ' + nick + ' :[!] Messages only forwarded from channel. Type "?help" for command list.' )
		elif ( ( sdata[1] == 'TOPIC' ) and ( ( sdata[2] == self.channel ) ) ):
			#	Someone changed the topic
			#	:Nick!ident@host.example.com TOPIC ##loafyland :Mary had a little lamb
			#	\__________[0]_____________/ \[1]/ \___[2]___/ \_______[3:]__________/
			temp_outbox = ' '.join( sdata[3:] ).replace( ':', '', 1 )
			temp_outbox = '§8[#] New IRC channel topic:§b ' + temp_outbox
			self.outbox.append( temp_outbox )
		elif sdata[1] == 'JOIN' and sdata[2].replace( ':', '', 1 ) == self.channel:
			#	Someone joined the channel
			#	:Nick!ident@host.example.com JOIN :##loafyland
			#	\__________[0]_____________/ \[1]/ \___[2]___/
			nick = sdata[0].replace( ':', '', 1 ).split( '!' )[0]
			temp_outbox = '§8[#] §7' + nick + '§8 has joined the IRC channel.'
			self.outbox.append( temp_outbox )
		elif sdata[1] == 'PART' and sdata[2].replace( ':', '', 1 ) == self.channel:
			#	Someone left the channel
			#	:Nick!ident@host.example.com PART ##loafyland :Reason
			#	\__________[0]_____________/ \[1]/\___[2]___/ \_[3]_/
			nick = sdata[0].replace( ':', '', 1 ).split( '!' )[0]
			temp_outbox = '§8[#] §7' + nick + '§8 has left the IRC channel.'
			self.outbox.append( temp_outbox )
		elif sdata[1] == 'KICK' and sdata[2].replace( ':', '', 1 ) == self.channel:
			#	Nick1 has kicked Nick2 out of the channel
			#	:Nick1!ident@host.example.com KICK ##loafyland Nick2 :Reason
			#	\_______[0] (Kicker)________/ \[1]/\___[2]___/ \[3]/ \_[4]_/
			nick = sdata[3].replace( ':', '', 1 ).split( '!' )[0]
			temp_outbox = '§8[#] §7' + nick + '§8 was kicked from the IRC channel.'
			self.outbox.append( temp_outbox )
		return( self.data )

	def say( self, text ):
		self.send( 'PRIVMSG ' + self.channel + ' :' + text )

	def parse_data( self ):
		self.data = self.buffer + self.data
		self.events = self.data.split( '\n' )
		self.buffer = self.events.pop()

	def send( self, text ):
		print ( 'IRC < ' + text )
		text += '\r\n'
		tosend = len( text )
		tosend -= self.socket.send( text )
		while tosend:
			select.select( [], [ self.socket ], [] )
			text = text[tosend:]
			tosend -= self.socket.send( text )

	def join( self ):
		if self.join_ok:
			print( 'Attempting to join ' + self.channel )
			self.send( 'JOIN ' + self.channel )
			self.status['joined'] = True
		
# Wrapper class around IRC.say() to send a private reponse to commands from a /MSG or /QUERY
class private_reply(object):
	def __init__( self, irc, nick ):
		self.irc = irc
		self.nick = nick
		
	def say( self, text ):
		self.irc.send( 'PRIVMSG ' + self.nick + ' :' + text )
