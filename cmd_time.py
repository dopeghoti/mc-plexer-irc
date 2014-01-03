#!/usr/bin/python
# coding=UTF-8
import os
import bisect
import random
import nbt

# Pathname to the level.dat file
level_file = '/home/minecraft/loafy/level.dat'


# Lookup table for time-of-day
names = [
	( 0	, [ "Morning" ] ),
	( 2250	, [ "Brunchtime" ] ),
	( 3500	, [ "Elevensies" ] ),
	( 5000	, [ "Noon", "Midday" ] ),
	( 6500	, [ "Teatime", "Afternoon" ] ),
	( 8000	, [ "Happy Hour" ] ),
	( 9500	, [ "Evening", "Suppertime", "Dinnertime" ] ),
	( 12000	, [ "Dusk", "Sunset", "Nightfall" ] ),
	( 14000	, [ "the Dark of Night", "Nighttime" ] ),
	( 15500	, [ "the Witching Hour" ] ),
	( 17000	, [ "Midnight" ] ),
	( 19000	, [ "the Hour of the Wolf" ] ),
	( 20500	, [ "the Wee Hours of the Morn" ] ),
	( 22200	, [ "Dawn", "Sunrise", "Daybreak" ] ),
]
names.sort()

# Initialization
random.seed()

class time_listener(object):
	def __init__( self, reply ):
		self.reply = reply

	def notify_save( self ):
		global names
		data = nbt.NBTFile(level_file)["Data"]

		time = data["DayTime"].value % 24000
		rain = data["raining"].value
		thunder = data["thundering"].value

		index = bisect.bisect( names, ( time, ) )
		name = random.choice( names[index - 1][1] )
		text = "[*] 'Tis " + name + " in Loafyland with "

		if rain:
			if thunder:
				text += "a severe thunderstorm warning."
			else:
				text += "a chance of showers."
		else:
			text += "partly cloudy skies."

		self.reply.say( text )

