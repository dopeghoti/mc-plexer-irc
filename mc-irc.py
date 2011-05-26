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

# So, let's connect to IRC!
print( 'Attempting to connect to IRC' )
irc_conn = irc_class.IRC( irc_server, irc_port, irc_nick, irc_channel )

if( irc_conn.status['connected'] ):
	sock_list.append( irc_conn.socket )

# And now, let's connect to the Minecraft Multiplexer
# TODO: Exception handling for Plexer not being there to connect to
print( 'Attempting to connect to Minecraft Multiplexer' )
mc_conn = mp_class.multiplexer_connection( '/home/minecraft/tmp/plexer.sock', None, mc_password )
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
					mc_conn.say( message )
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

