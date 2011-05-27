#!/usr/bin/python
# coding=UTF-8
import os
import sys
import time

# Directory with player profiles
profile_dir = '/home/minecraft/world/players'

# How many players to show if no player name was given to query_last()
query_last_num = 5

def format_time( file_time ):
	seconds = int( time.time() - file_time )

	if seconds < 0:
		return "[bad timestamp]"

	minutes = seconds // 60
	hours = minutes // 60
	days = hours // 24

	seconds %= 60
	minutes %= 60
	hours %= 24

	if days >= 365:
		return time.strftime( "%b %d, %Y", time.localtime( file_time ) )
	elif days > 30:
		return time.strftime( "%b %d", time.localtime( file_time ) )
	elif days > 1:
		return "%d days ago" % days
	elif days == 1:
		return "1 day ago"
	elif hours > 1:
		return "%d hours ago" % hours
	elif hours == 1:
		return "1 hour ago"
	elif minutes > 1:
		return "%d mins ago" % minutes
	elif minutes == 1:
		return "1 min ago"
	elif seconds > 1:
		return "%d secs ago" % seconds
	elif seconds == 1:
		return "1 sec ago"
	else:
		return "now"


def query_last( reply, args ):
	files_orig_case = [ x for x in os.listdir( profile_dir ) if x.endswith(".dat") ]

	if len(args):
		player = args[0]
	
		files_lower_case = [ x.lower() for x in files_orig_case ]
		player_lower_file = player.lower() + ".dat"

		if player_lower_file in files_lower_case:
			index = files_lower_case.index( player_lower_file )
			file_name = files_orig_case[ index ]
			file_path = profile_dir + os.sep + file_name

			file_time = os.stat( file_path ).st_mtime
			ago_time = format_time( file_time )
			player_proper_name = file_name.replace( ".dat", "" )

			reply.say( "Player %s last seen %s." % ( player_proper_name, ago_time ) )
		else:
			reply.say( "Player %s not found on server." % player )

	else:
		file_times = [ os.stat( profile_dir + os.sep + x ).st_mtime for x in files_orig_case ]

		results = zip( file_times, files_orig_case )
		results.sort()
		results.reverse()
		results = results[ :query_last_num ]

		text = []
		for file_time, file_name in results:
			player = file_name.replace( ".dat", "" )
			ago_time = format_time( file_time )
			text.append( "%s (%s)" % ( player, ago_time ) )

		count = len( text )
		reply.say( "Last %d players: %s" % ( count, ", ".join( text ) ) )
