#!/usr/bin/python
import socket
import multiplexlib
import time
import sys
import string
import select

import irc_class

# TODO: External configuration files

# IRC configuration settings
irc_server = 'irc.example.com'
irc_nick = 'Nick'
irc_port = 6667
irc_channel = '#channel'

# Multiplexer configuration settings
mc_socket = '/path/to/your/plexer.sock'
mc_port = 9001
mc_password = 'password'

# So, let's connect to IRC!
print( 'Attempting to connect to IRC' )
conn = irc_class.IRC( irc_server, irc_port, irc_nick, irc_channel )

# And now, let's connect to the Minecraft Multiplexer
# TODO: Exception handling for Plexer not being there to connect to
# TODO: Make this a class like IRC.
print( 'Attempting to connect to Minecraft Multiplexer' )
ml = multiplexlib.MinecraftRemote(socket.AF_UNIX, mc_socket, mc_port, mc_password )
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

		if conn.status['joined'] == False:
			conn.join()

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
    conn.disconnect( 'Process caught SIGINT' )
except Exception, e:
    print 'Got exception: ' + e.__str__()

