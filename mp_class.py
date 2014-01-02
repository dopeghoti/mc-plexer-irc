#!/usr/bin/python
# coding=UTF-8
import socket
import time
import sys
import string
import select
import mc_blocks
import cmd_last
import re

# Multiplexer configuration settings
mc_socket = '/home/minecraft/tmp/plexer.sock'
from mc_private import *

# Characters recognized as a command prefix in Minecraft (not including '/' for private cmds)
CMD_PREFIX = [ '?', '!' ]

class multiplexer_connection:

	def __init__( self, dispatcher, sockfile, port = None, password = None ):
		self.outbox = []
		self.socket = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
		self.status = { 'connected' : False, 'authenticated' : False }
		self.buffer = ''
		self.data = ''
		self.events = []

		self.dispatcher = dispatcher
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
				self.send( self.password + '\r\n' )
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
		self.send( '' )
		self.status['connected'] = False
		self.status['authenticated'] = False
		self.socket.close()

	def cmd( self, text ):
		print( 'Sending command to Multiplexer: ' + text )
		self.send( text + '\r\n' )

	def send( self, text ):
		tosend = len( text )
		tosend -= self.socket.send( text )
		while tosend:
			select.select( [], [ self.socket ], [] )
			text = text[tosend:]
			tosend -= self.socket.send( text )

	def say( self, text, cmd = 'say', maxlen = 99, surline = '[^] ' ):
		line = ''
		writeline = False
		#	Find "words" that are too long, and redact them.
		wordlist = [ word if len( word ) < 85 else word[:4] + '§8[...]§a' + word[-4:] for word in text.split() ]

		#	Now to make it MC-size bites.
		#for word in wordlist:
			#if len( line ) + len( word ) > 100:
				#if writeline:
					#self.cmd( 'say ' + line )
					#line = surline
					#writeline = False
				#else:
					##	We should never be here, but cry if we are.
					#print( 'MCM> Something went wrong in mp_class.say() with line:' )
					#print( 'MCM> ' + text )
			#else:
				#line = line + word + ' '
				#writeline = True
		#if writeline:
			#self.cmd( 'say ' + line )

		#	Tack a False onto the end; watch for it to stop spitting out text.
		wordlist.append( False )

		while wordlist:
			curr_word = wordlist.pop( 0 )
			if not curr_word or len( line ) + len( curr_word ) > maxlen:
				#self.cmd( cmd + ' ' + line )
				self.cmd( cmd + line )
				line = ' ' + surline
			if curr_word:
				line = line + ' ' + curr_word



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
				if len(eparts) > 2 and self.dispatcher.notify_raw( eparts ):
					# If dispatcher was waiting to parse raw output then don't handle it further here
					pass
				elif len(eparts) > 3:
					if eparts[3][0] == '<' or eparts[3] == '[CONSOLE]':
						# Looks like someone's talking.
						talker  = eparts[3][1:-1]	# strip the leading and trailing brackets
						chatter = ' '.join(eparts[4:])
						if chatter:
							# Bot Commands begin with one and only one prefix character
							if chatter[0:1] in CMD_PREFIX and not chatter[1:2] in CMD_PREFIX:
								keyword = chatter.split(' ')[0].upper()
								args = chatter.split(' ')[1:]
								self.dispatcher.notify_cmd( self, talker, keyword, args )
							elif len(chatter) > 5 and ( chatter.upper()[-5:] == '> IRC' or chatter.upper()[-4:] == '>IRC' ):
								# Someone is talking to IRC, old-school.
								chatter = chatter[:-3]
								self.outbox.append( '14<9' + talker + '14> 11' + chatter )
								self.cmd( 'tell ' + talker + ' [*] That notation is no longer needed.' )
							else:
								if talker != "CONSOLE":
									#	chatter = chatter[:-3]
									self.outbox.append( '14<9' + talker + '14> 11' + chatter )

					elif eparts[3][0] == "*":
						#	Someone is acting
						#	self.outbox.append (' action stub ' ) 
                                                talker  = eparts[4]       # strip the leading and trailing brackets
						chatter = ' '.join(eparts[5:])
						self.outbox.append( ' 11* 9' + talker + ' 11' + chatter )
					elif ' '.join(eparts[4:7]) == 'issued server command:' and len(eparts) > 7:
						talker = eparts[3]
						keyword = '?' + eparts[7].upper()
						args = eparts[8:]
						self.dispatcher.notify_cmd( private_reply( self, talker ), talker, keyword, args )
					elif ' '.join(eparts[4:6]) == 'tried command:' and len(eparts) > 6:
						talker = eparts[3]
						keyword = '?' + eparts[6].upper()
						args = eparts[7:]
						self.dispatcher.notify_cmd( private_reply( self, talker ), talker, keyword, args )
					elif ' '.join(eparts[6:8]) == 'players online:':
						self.dispatcher.notify_players()
					elif ' '.join(eparts[4:6]) == 'logged in':
						self.dispatcher.notify_login( eparts[3].split('[')[0] )
					elif ' '.join(eparts[4:6]) == 'lost connection:':
						self.dispatcher.notify_logout( eparts[3] )
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


# Wrapper class around multiplexer_connection.say() to send a private /TELL response to commands issued
# privately in game with a / instead of a ?
class private_reply(object):
	def __init__( self, mp, talker ):
		self.mp = mp
		self.talker = talker
		
	def say( self, text ):
		# maxlen: 100 - "CONSOLE whispers " = 83
		self.mp.say( text, cmd = 'tell ' + self.talker, maxlen = 83 )
