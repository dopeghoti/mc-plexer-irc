#!/usr/bin/python
# coding=UTF-8
import socket
#import multiplexlib
import time
import sys
import string
import select

import irc_class
import mp_class

import cmd_last
import mc_blocks

# TODO: External configuration files

# IRC configuration settings
irc_server = 'irc.freenode.net'
irc_nick = 'VoxelHead'
irc_port = 6667
#irc_channel = '###linkulator'
#irc_channel = '##crawl-offtopic'
irc_channel = '##loafyland'

# Multiplexer configuration settings
mc_socket = '/home/minecraft/tmp/plexer.sock'
mc_port = 9001
mc_password = 'aardvark'

sock_list = []


# Common dispatcher class for commands from in game and from IRC
class cmd_dispatcher:
	def __init__( self ):
		self.online_player_listeners = []

	def request_players( self, listener ):
		# Called by bot commands to register a listener for output of server "list" command
		global mc_conn
		self.online_player_listeners.append( listener )
		mc_conn.cmd('list')

	def notify_players( self, players ):
		# Someone asked who's playing. Relay it to one of the listening objects
		if len(self.online_player_listeners):
			listener = self.online_player_listeners[0]
			del self.online_player_listeners[0]
			listener.notify_players( players )

	def notify_login( self, player ):
		# Touch profile timestamp to record login time for ?who
		cmd_last.notify_login( player )

	def notify_cmd( self, reply, talker, keyword, args ):
		botcmds = ['?ID', '?WHO', '?LOAD', '?MAP', '?MUMBLE', '?LAST', '?SERVER', '!REHASH']
		if keyword in ["?HELP"]:
			reply.say( '[*] Available commands:' )
			reply.say( '[*] ' + ' '.join(botcmds) )
		elif keyword in ['?ID']:
			mc_blocks.lookup( reply, " ".join( args ) )
		elif keyword in ['?WHO', '?W', '?PLAYERS']:
			self.request_players( cmd_last.who_listener( reply ) )
		elif keyword in ['?MUMBLE']:
			reply.say( '[*] Mumble server at wold.its.lsu.edu' )
			reply.say( '[*] Contact DopeGhoti, Thvortex, or Sunfall (Phil_Bordelon) for password.')
		elif keyword in ['?LOAD']:
			u = open( '/proc/loadavg', 'r' )
			l = u.readline().split()[0]
			u.close()
			reply.say( '[*] Current system load is ' + l )
		elif keyword in ['?MAP', '?GPS', '?SHOW']:
			if len( args ) == 2:
				#	We need to present a Y coordinate.  Assume ground-level
				mapurl = 'http://minecraft.hfbgaming.com/?x=' + str( args[0] ) + '&y=64&z=' + str( args[1] ) + '&zoom=max'
			elif len( args ) == 3:
				mapurl = 'http://minecraft.hfbgaming.com/?x=' + str( args[0] ) + '&y=' + str( args[1] ) + '&z=' + str( args[2] ) + '&zoom=max'
			elif len( args ) == 0:
				#	No paramaters. Just give the URL
				mapurl = 'http://minecraft.hfbgaming.com/'
			else:
				#	No idea what the user would be asking for. Help em.
				mapurl = 'Usage: ' + keyword + ' X [Y] Z'
			reply.say( mapurl )
		elif keyword in ['?WTF', '?TIME']:
			reply.say( '[*] Not yet implemented, ' + talker )
		elif keyword in ['?LAST']:
			# Note: list(args) makes a shallow copy in case caller changes args later
			self.request_players( cmd_last.last_listener( reply, list(args) ) )
		elif keyword in ['?SERVER', '?MINECRAFT']:
			reply.say( '[*] The minecraft server can be found at ghoti.dyndns.org.' )
			reply.say( '[*] For more information, say "#link 673" in channel.' )
		elif keyword in ['!REHASH']:
			global irc_conn
			reply.say( '[*] Rehashing.' )
			irc_conn.disconnect( 'Asked to rehash' )


dispatcher = cmd_dispatcher()

# So, let's connect to IRC!
print( 'Attempting to connect to IRC' )
irc_conn = irc_class.IRC( dispatcher, irc_server, irc_port, irc_nick, irc_channel )

if( irc_conn.status['connected'] ):
	sock_list.append( irc_conn.socket )

# And now, let's connect to the Minecraft Multiplexer
# TODO: Exception handling for Plexer not being there to connect to
print( 'Attempting to connect to Minecraft Multiplexer' )
mc_conn = mp_class.multiplexer_connection( dispatcher, '/home/minecraft/tmp/plexer.sock', None, mc_password )
mc_conn.connect()

if( mc_conn.status['connected'] ):
	sock_list.append( mc_conn.socket )
	mc_conn.cmd( 'say §7[§2!§7] VoxelHead Online.')

# sock_list = [ mc_conn.socket, irc_conn.socket ]

try:
	while irc_conn.status['connected'] and mc_conn.status['connected']:
		( sock_out, sock_in, sock_exception ) = select.select( sock_list, [], [] )
		# See if there is anything pending from Minecraft or IRC
		for s in sock_out:
			if s == mc_conn.socket:
				mc_conn.cycle()
			if s == irc_conn.socket:
				irc_conn.cycle()

		# Make sure the IRC connection hasn't died on us
		if( irc_conn.status['connected'] == False ):
			irc_conn.connect()

		# See if there is anything pending _for_ IRC
		if irc_conn.status['joined'] == False:
			irc_conn.join()
		if( len( mc_conn.outbox ) > 0 ):
			for message in mc_conn.outbox:
				irc_conn.say( message )
			mc_conn.outbox = []

		# See if there is anything pending _for_ Minecraft
		if(len( irc_conn.outbox ) > 0):
			for message in irc_conn.outbox:
				print( 'MCM < ' +  message )
				mparts = message.split()
				#print( repr ( mparts[2] ) )
				if len( mparts ) > 2:
					if mparts[2][0] == "\x01":
						if mparts[2] == '\x01ACTION':
							message = mparts[0] + " §a* " + mparts[1].replace('<','').replace('>','') + " " + " ".join( mparts[ 3: ] )
					mc_conn.say( message, surline = '§8[^]§a' )
			irc_conn.outbox = []

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
    mc_conn.cmd( 'say §7[§c!§7] VoxelHead Offline.' )
    irc_conn.disconnect( 'Process caught SIGINT' )
#except Exception, e:
#    print 'Got exception: ' + e.__str__()

