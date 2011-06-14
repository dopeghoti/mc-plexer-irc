#!/usr/bin/python
# coding=UTF-8
import os
import re
import sys
import time

# Directory with player profiles
profile_dir = '/home/minecraft/loafy/players'

# Default number of players returned by ?last command if no arguments were given
default_num_last = 5


class who_listener(object):
	def __init__( self, reply ):
		self.reply = reply

	def notify_players( self, players ):
		file_names = [ x + ".dat" for x in players ]
		text = format_players( file_names, 0, predate = "since ", pretime = "for " )

		if len(text):
			self.reply.say( '[*] Currently playing: ' + ', '.join( text ) )
		else:
			self.reply.say( '[*] Nobody is currently playing' )


class last_listener(object):
	def __init__( self, reply, args ):
		self.reply = reply
		self.args = args

	def notify_players( self, players ):
		players = set( x + ".dat" for x in players )
		files_orig_case = [ x for x in os.listdir( profile_dir ) if x.endswith(".dat") and x not in players ]

		seconds = 0	# Time limit for "?last <N> s[econds]|m[inutes]|h[ours]|d[ays]" in seconds
		past = ""	# Textual description of the time interval represented by "seconds" var
		limit = 0	# Max number of players for "?last <N>" or the default for "?last"
		search = ""	# Player name search string for "?last <name>"
		
		args = " ".join( self.args ).strip()
		match = re.match(r"(\d+)\s*([a-z]+)", args.lower())
		if args.isdigit():
			limit = int(args)
			if limit == 0:
				self.reply.say( '[!] Player count cannot be zero' )
				return
		elif match:
			number, units = match.group(1, 2)
			number = int(number)
			if number == 0:
				self.reply.say( '[!] Time interval cannot be zero' )
				return
			if "seconds".startswith(units):
				seconds = number
				past = "second" if number == 1 else "%d seconds" % number
			elif "minutes".startswith(units):
				seconds = number * 60 + 59
				past = "minute" if number == 1 else "%d minutes" % number
			elif "hours".startswith(units):
				seconds = number * 3600 + 3599
				past = "hour" if number == 1 else "%d hours" % number
			elif "days".startswith(units):
				seconds = number * 86400 + 86399
				past = "day" if number == 1 else "%d days"% number
			else:
				self.reply.say( '[!] Unrecognized time unit "%s"' % units )
				return
		elif args:
			search = args
		else:
			limit = default_num_last

		online_matches = search_players( players, search )
		offline_matches = search_players( files_orig_case, search )
		online_players = [ x.replace( ".dat", "" ) + " (online)" for x in online_matches ]
		offline_players = format_players( offline_matches, seconds, posttime = " ago" )
		all_players = online_players + offline_players
		if limit:
			all_players = all_players[ :limit ]
		count = len(all_players)
		player = "player" if count == 1 else "players"

		if search:
			if count:
				text = '[*] Last %s named "%s": ' % ( player, search )
			else:
				text = '[*] No players named "%s" were found' % search
		elif seconds:
			if count:
				text = '[*] Last %s in the past %s: ' % ( player, past )
			else:
				text = '[*] Nobody has played in the past %s' % past
		else:
			if count:
				if limit > 1:
					text = '[*] Last %d players: ' % limit
				else:
					text = '[*] Last 1 player: '
			else:
				text = '[*] No players found on server'
		
		self.reply.say( text + ', '.join( all_players ) )


def format_time( file_time, seconds, pretime = "", posttime = "", predate = "", postdate = "" ):
	if seconds < 0:
		return "[bad timestamp]"

	minutes = seconds // 60
	hours = minutes // 60
	days = hours // 24

	seconds %= 60
	minutes %= 60
	hours %= 24

	if days >= 365:
		text = time.strftime( "%b %d, %Y", time.localtime( file_time ) )
		return predate + text + postdate		
	elif days > 30:
		text = time.strftime( "%b %d", time.localtime( file_time ) )
		return predate + text + postdate
	elif days > 1:
		return pretime + "%d days" % days + posttime
	elif days == 1:
		return pretime + "1 day" + posttime
	elif hours > 1:
		return pretime + "%d hours" % hours + posttime
	elif hours == 1:
		return pretime + "1 hour" + posttime
	elif minutes > 1:
		return pretime + "%d mins" % minutes + posttime
	elif minutes == 1:
		return pretime + "1 min" + posttime
	elif seconds > 1:
		return pretime + "%d secs" % seconds + posttime
	elif seconds == 1:
		return pretime + "1 sec" + posttime
	else:
		return pretime + "less than 1 sec" + posttime

def search_players( file_names, player ):
	player = player.lower()
	results = []
	for x in file_names:
		if player in x.lower().replace( ".dat", "" ):
			results.append( x )
	return results
	#lookup_list = [ ( x.lower().replace( ".dat", "" ), x ) for x in file_names ]	
	#player = player.lower()
	#return [ y for x, y in lookup_list if player in x ]

def format_players( file_names, max_interval, **format_time_args ):
	file_times = [ os.stat( profile_dir + os.sep + x ).st_mtime for x in file_names ]

	results = zip( file_times, file_names )
	results.sort()
	results.reverse()

	text = []
	now = time.time()
	for file_time, file_name in results:
		interval = int( now - file_time )
		if max_interval and interval > max_interval:
			break
		player = file_name.replace( ".dat", "" )
		ago_time = format_time( file_time, interval, **format_time_args )
		text.append( "%s (%s)" % ( player, ago_time ) )

	return text


def notify_login( player ):
	os.utime( profile_dir + os.sep + player + ".dat", None )

