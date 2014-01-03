#!/usr/bin/python
# coding=UTF-8
import traceback

import cmd_last
import mc_blocks
import cmd_time
import cmd_rehash

# Context manager to catch unhandled exceptions and report error message to sender
class exc_manager:
	def __init__( self, reply = None ):
		self.reply = reply
		
	def __enter__( self ):
		pass
		
	def __exit__( self, exc_type, exc_val, exc_tb ):
		if exc_type:
			traceback.print_exception( exc_type, exc_val, exc_tb )
			if self.reply:
				text = traceback.format_exception_only( exc_type, exc_val )
				self.reply.say( '[!] ' + text[-1] )
		return True

# Common dispatcher class for commands from in game and from IRC
class dispatcher:
	def __init__( self ):
		self.online_player_listeners = []
		self.save_listeners = []
		self.raw_listeners = []

	def request_players( self, listener ):
		# Called by bot commands to register a listener for output of server "list" command
		# Since the "list" command is now split into two parts, register a raw handler ir
		self.online_player_listeners.append( listener )
		self.mc_conn.cmd('list')

	def request_save( self, listener ):
		# Called by bot commands to register a listener for completion of "Save-all" command
		self.save_listeners.append( listener )
		self.mc_conn.cmd('save-all')

	def notify_raw( self, eparts ):
		# Someone asked who's playing. Handle parsing of the raw 2nd line of "list" command output
		if len(self.raw_listeners):
			listener = self.raw_listeners[0]
			del self.raw_listeners[0]
			with exc_manager( listener.reply ):
				listener.notify_raw( eparts )
			return True   # Inhibit further handling of raw text line in caller
		else:
			return False  # No raw listeners pending so let caller handle the raw line

	def notify_save( self ):
		# Someone was waiting for "save-all" to complete; notify them
		if len(self.save_listeners):
			listener = self.save_listeners[0]
			del self.save_listeners[0]
			with exc_manager( listener.reply ):
				listener.notify_save()

	def notify_players( self ):
		# Someone asked who's playing. Prepare raw listener to parse the actual list on the next line
		if len(self.online_player_listeners):
			listener = self.online_player_listeners[0]
			self.raw_listeners.append( listener )
			del self.online_player_listeners[0]

	def notify_login( self, player ):
		# Touch profile timestamp to record login time for ?who and print login msg on IRC
		with exc_manager():
			cmd_last.notify_login( player )
			self.irc_conn.say( "14[*] 15%s14 has arrived in Loafyland." % player )

	def notify_logout( self, player ):
		# Print logout msg on IRC
		with exc_manager():
			self.irc_conn.say( "14[*] 15%s14 has departed from Loafyland." % player )

	def notify_cmd( self, reply, talker, keyword, args ):
		with exc_manager( reply ):
			self.__notify_cmd( reply, talker, keyword, args )

	def __notify_cmd( self, reply, talker, keyword, args ):
		botcmds = ['?ID', '?WHO', '?LOAD', '?MAP', '?MUMBLE', '?LAST', '?SERVER', '?TIME', '!REHASH']
		if keyword in ['!REHASH']:
			if args:
				for name in args:
					with exc_manager( reply ):
						reply.say( '[*] Rehashing module "%s"' % name )
						cmd_rehash.do_rehash( reply, name )
			else:
				reply.say( '[*] Rehashing everything.' )
				self.irc_conn.disconnect( 'Asked to rehash' )
		elif keyword in ['?HELP']:
			reply.say( '[*] Available commands:' )
			reply.say( '[*] ' + ' '.join(botcmds) )
		elif keyword in ['?ID']:
			mc_blocks.lookup( reply, " ".join( args ) )
		elif keyword in ['?WHO', '?W', '?PLAYERS']:
			self.request_players( cmd_last.who_listener( reply ) )
		elif keyword in ['?MUMBLE']:
			reply.say( '[*] Mumble server at ripley.thenexusproject.org:64738' )
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
		elif keyword in ['?TIME']:
			# Need to "save-all" so level.dat is updated with latest time
			self.request_save( cmd_time.time_listener( reply ) )
		elif keyword in ['?LAST']:
			# Note: list(args) makes a shallow copy in case caller changes args later
			self.request_players( cmd_last.last_listener( reply, list(args) ) )
		elif keyword in ['?SERVER', '?MINECRAFT']:
			reply.say( '[*] The minecraft server can be found at ghoti.dyndns.org.' )
			reply.say( '[*] For more information, say "#link 673" in channel.' )
