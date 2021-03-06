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


class player_list_listener(object):
	def __init__( self, reply ):
		self.reply = reply

	def notify_raw( self, eparts ):
		r = re.compile( ",$" )
		players = [ r.sub( "", x ) for x in eparts[3:] ]
		self.notify_players( players )


class who_listener(player_list_listener):
	def __init__( self, reply ):
		super(who_listener, self).__init__( reply )

	def notify_players( self, players ):
		if len(players):
			self.reply.say( '[*] Currently playing: ' + ', '.join( players ) )
		else:
			self.reply.say( '[*] No players currently online' )


class last_listener(player_list_listener):
	def __init__( self, reply, args ):
		super(last_listener, self).__init__( reply )
		self.args = args

	def notify_players( self, players ):
		players = set( x + ".dat" for x in players )
		files_orig_case = [ x for x in os.listdir( profile_dir ) if x.endswith(".dat") and x not in players ]

		seconds = 0	# Time limit for "?last <N> s[econds]|m[inutes]|h[ours]|d[ays]" in seconds
		past = ""	# Textual description of the time interval represented by "seconds" var
		limit = 0	# Max number of players for "?last <N>" or the default for "?last"
		search = ""	# Player name search string for "?last <name>"

		for arg in self.args:
			match = re.match( r"(\d+)(\D+)", arg.lower() )

			if arg.isdigit():
				limit = int(arg)
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
					past = "day" if number == 1 else "%d days" % number
				elif "weeks".startswith(units):
					seconds = number * 7 * 86400 + 86399
					past = "week" if number == 1 else "%d weeks" % number
				elif "years".startswith(units):
					seconds = int( round( number * 365.25 * 86400 + 86399 ) )
					past = "year" if number == 1 else "%d years" % number
				else:
					self.reply.say( '[!] Unrecognized time unit "%s"' % units )
					return
			else:
				search = arg

		if not seconds and not limit and not search:
			limit = default_num_last

		online_matches = search_players( players, search )
		offline_matches = search_players( files_orig_case, search )
		online_players = [ x.replace( ".dat", "" ) + " (online)" for x in online_matches ]
		offline_players = format_players( offline_matches, seconds, posttime = " ago" )
		all_players = online_players + offline_players
		if limit:
			all_players = all_players[ :limit ]
		count = len(all_players)

		if count:
			text = '[*] Last'
			if limit == 1:
				text += ' 1 player'
			elif limit:
				text += ' %d players' % limit
			elif count == 1:
				text += ' player'
			else:
				text += ' players'
		else:
			text = '[*] No players'

		if seconds:
			text += ' in the past %s' % past
		if search:
			text += ' matching "%s"' % search

		if count:
			text += ': '
		else:
			text += ' were found'

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

