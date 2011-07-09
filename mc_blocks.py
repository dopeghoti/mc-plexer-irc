#!/usr/bin/python
# coding=UTF-8
#	A dictionary of block and item code types
import random


# Maximum number of id numbers returned by inexact substring match
lookup_max_num = 5


random.seed()
#	Initialization

def blkdefine( code, desc ):
	global block
	block[code] = []
	for d in desc:
		block[code].append(d)

def describe( id ):
	global block
	return random.choice( block[id] )

def search( data ):
	found = []
	for b in block:
		for text in block[b]:
			if data == text:
				return [b]
				break
			if data in text.lower().split():
				found.append(b)
				break
	return found

def lookup( reply, data ):
	global block
	data = data.strip().lower()
	if not data:
		# No query string specified. Print usage info
		reply.say( '[*] Usage: ?ID number|description' )
	elif data.isdigit():
		#	We've been given a number; loop up the corresponding block and return its first name
		if int(data) in block:
			reply.say( '[*] Match: ' + describe( int(data) ) )
		else:
			reply.say( '[*] No Match' )
	else:
		#	Must be a string.  See it matches any of the blocks we know
		found = search(data)
		if len(found) == 0:
			reply.say( '[*] No Match' )
		elif len(found) > lookup_max_num:
			reply.say( '[*] Too many (%d) matches. Be more specific.' % len(found) )
		else:
			results = [ "%d (%s)" % ( b, describe(b) ) for b in found ]
			label = "Match: " if len(found) == 1 else "Matches: "
			reply.say( '[*] ' + label + ", ".join( results ) )


block = {}

#	Blocks
blkdefine(    0, ['air'] )
blkdefine(    1, ['stone', 'smooth stone', 'concrete', 'natural stone', 'smooth', 'stone block'] )
blkdefine(    2, ['grass', 'sod', 'grassy dirt', 'grassy soil'] )
blkdefine(    3, ['dirt', 'soil'] )
blkdefine(    4, ['cobblestone', 'cobble', 'cobble stone'] )
blkdefine(    5, ['planks', 'wood planks', 'plank', 'wooden planks', 'wood board', 'wooden boards'] )
blkdefine(    6, ['sapling'] )
blkdefine(    7, ['adminium', 'bedrock', 'modstone', 'adminite'] )
blkdefine(    8, ['water', 'flowing water'] )
blkdefine(    9, ['spring', 'water source', 'still water', 'stationary water'] )
blkdefine(   10, ['flowing magma', 'magma flow', 'flowing lava', 'lava flow'] )
blkdefine(   11, ['magma', 'lava', 'magma source', 'lava source'] )
blkdefine(   12, ['sand'] )
blkdefine(   13, ['flint'] )
blkdefine(   14, ['gold ore', 'raw gold', 'vitamin g', 'unrefined vitamin g'] )
blkdefine(   15, ['iron ore', 'raw iron', 'vitamin i', 'unrefined vitamin i'] )
blkdefine(   16, ['coal ore', 'raw coal', 'vitamin c', 'unrefined vitamin c'] )
blkdefine(   17, ['wood', 'log', 'lumber'] )
blkdefine(   18, ['leaves', 'foliage', 'leaf'] )
#blkdefine(   19, ['sponge'] )
blkdefine(   20, ['glass', 'window'] )
blkdefine(   21, ['lapis lazuli ore', 'raw lapis lazuli', 'vitamin l'] )
blkdefine(   22, ['lapis lazuli block', 'concentrated vitamin l'] )
blkdefine(   23, ['dispenser'] )
blkdefine(   24, ['sandstone', 'sand stone'] )
blkdefine(   25, ['note block', 'music block', 'sound block', 'music box', 'musicbox'] )
#blkdefine(   26, ['bed', 'mattress'] )
blkdefine(   27, ['powered rails', 'powered tracks', 'powered rail', 'powered track'] )
blkdefine(   28, ['detector rails', 'detector tracks', 'detector rail', 'detector track'] )
blkdefine(   29, ['sticky piston', 'slimy piston'] )
blkdefine(   30, ['cobweb', 'web'] )
blkdefine(   31, ['tall grass', 'grass'] )
blkdefine(   32, ['dead shrubs', 'shrubs', 'shrub' ,'dead shrub'] )
blkdefine(   33, ['piston'] )
blkdefine(   35, ['white wool', 'wool'] )
blkdefine(   37, ['yellow flower', 'dandelion'] )
blkdefine(   38, ['red flower', 'red rose', 'rose'] )
blkdefine(   39, ['brown mushroom', 'brown shroom'] )
blkdefine(   40, ['red mushroom', 'red shroom'] )
blkdefine(   41, ['gold block', 'concentrated vitamin g'] )
blkdefine(   42, ['iron block', 'concentrated vitamin i'] )
blkdefine(   43, ['double stone slab', 'double halfstep', 'double slab'] )
blkdefine(   44, ['stone slab', 'halfstep'] )
blkdefine(   45, ['brick block', 'bricks', 'masonry', 'brick wall'] )
blkdefine(   46, ['tnt', 'explosives', 'dynamite'] )
blkdefine(   47, ['bookshelf', 'shelf'] )
blkdefine(   48, ['mossy cobblestone', 'mossy cobble', 'moss stone', 'mossy stone', 'mossy'] )
blkdefine(   49, ['obsidian', 'obby'] )
blkdefine(   50, ['torch'] )
blkdefine(   51, ['fire'] )
blkdefine(   52, ['spawner', 'monster spawner', 'cage'] )
blkdefine(   53, ['wooden stairs', 'wood stairs', 'wooden staircase', 'wood staircase', 'wooden stair', 'wood stair'] )
blkdefine(   54, ['chest', 'storage chest', 'locker'] )
#blkdefine(   55, ['redstone wire', 'wire'] )
blkdefine(   56, ['diamond ore', 'raw diamond', 'vitamin d', 'unrefined vitamin d'] )
blkdefine(   57, ['diamond block', 'concantrated vitamin d'] )
blkdefine(   58, ['workbench', 'crafting table'] )
#blkdefine(   59, ['crops', 'wheat'] )
#blkdefine(   60, ['tilled soil'] )
blkdefine(   61, ['furnace', 'forge', 'stove'] )
#blkdefine(   62, ['lit furnace', 'lit forge'] )
#blkdefine(   63, ['sign post', 'signpost'] )
#blkdefine(   64, ['wooden door', 'wood door'] )
#blkdefine(   65, ['ladder'] )
#blkdefine(   66, ['rails', 'tracks', 'rail', 'track'] )
blkdefine(   67, ['cobblestone stairs', 'stone stairs', 'cobblestone staircase', 'stone staircase', 'cobblestone stair', 'stone stair', 'cobble stair'] )
#blkdefine(   68, ['sign'] )
blkdefine(   69, ['lever', 'switch'] )
blkdefine(   70, ['stone pressure plate', 'stone plate', 'stone pad', 'stone pressure pad'] )
#blkdefine(   71, ['iron door'] )
blkdefine(   72, ['wood pressure plate', 'wood plate', 'wood pad', 'wood pressure pad', 'wooden pressure plate', 'wooden plate', 'wooden pad', 'wooden pressure pad'] )
blkdefine(   73, ['redstone ore'] )
blkdefine(   74, ['glowing redstone ore'] )
blkdefine(   75, ['redstone torch (off)'] )
blkdefine(   76, ['redstone torch (on)'] )
blkdefine(   77, ['button', 'stone button'] )
blkdefine(   78, ['snowfall', 'snow', 'fallen snow'] )
blkdefine(   79, ['ice', 'ice block'] )
blkdefine(   80, ['snow block'] )
blkdefine(   81, ['cactus', 'cacti'] )
blkdefine(   82, ['clay', 'clay block'] )
#blkdefine(   83, ['sugar cane', 'sugar', 'reeds', 'bamboo', 'shoots'] )
blkdefine(   84, ['jukebox', 'record player'] )
blkdefine(   85, ['fence', 'fencing'] )
blkdefine(   86, ['pumpkin'] )
blkdefine(   87, ['netherstone', 'netherrack', 'firestone', 'hellstone', 'bloodstone', 'nether stone', 'hell stone', 'blood stone' ] )
blkdefine(   88, ['soul sand', 'slow sand', 'soulsand', 'slowsand'] )
blkdefine(   89, ['glowstone', 'lightstone', 'glow stone', 'light stone'] )
#blkdefine(   90, ['portal'] )
blkdefine(   91, ['jack-o-lantern'] )
#blkdefine(   92, ['cake'] )
#blkdefine(   93, ['redstone repeater (off)'] )
#blkdefine(   94, ['redstone repeater (on)'] )
blkdefine(   96, ['trapdoor', 'hatch'] )

#	items
blkdefine(  256, ['iron shovel', 'iron spade', 'steel shovel', 'steel spade'] )
blkdefine(  257, ['iron pick', 'iron pickaxe', 'steel pick', 'steel pickaxe'] )
blkdefine(  258, ['iron axe', 'steel axe'] )
blkdefine(  259, ['flint and steel', 'firelighter', 'firestarter', 'fire lighter', 'fire starter'] )
blkdefine(  260, ['apple'] )
blkdefine(  261, ['bow'] )
blkdefine(  262, ['arrow'] )
blkdefine(  263, ['coal', 'natural coal'] )
blkdefine(  264, ['diamond', 'vitamin d pill'] )
blkdefine(  265, ['iron ingot', 'iron bar', 'steel ingot', 'steel bar', 'lard', 'refined vitamin i'] )
blkdefine(  266, ['gold ingot', 'gold bar', 'butter', 'refined vitamin g'] )
blkdefine(  267, ['iron sword', 'steel sword'] )
blkdefine(  268, ['wooden sword', 'wood sword', 'sharp stick'] )
blkdefine(  269, ['wooden shovel', 'wooden spade', 'wood shovel', 'wood spade'] )
blkdefine(  270, ['wooden pick', 'woodwn pickaxe', 'wood pick', 'wood pickaxe'] ) 
blkdefine(  271, ['wooden axe', 'wood axe'] )
blkdefine(  272, ['stone sword', 'rock sword'] )
blkdefine(  273, ['stone shovel', 'stone spade', 'rock shovel', 'rock spade'] )
blkdefine(  274, ['stone pick', 'rock pick', 'stone pickaxe', 'rock pickaxe'] )
blkdefine(  275, ['stone axe', 'rock axe'] )
blkdefine(  276, ['diamond sword'] )
blkdefine(  277, ['diamond shovel', 'diamond spade'] )
blkdefine(  278, ['diamond pick', 'diamond pickaxe'] )
blkdefine(  279, ['diamond axe'] )
blkdefine(  280, ['stick', 'sticks'] )
blkdefine(  281, ['bowl', 'wood bowl', 'wooden bowl'] )
blkdefine(  282, ['soup', 'mushroom soup'] )
blkdefine(  283, ['golden sword', 'gold sword'] )
blkdefine(  284, ['golden shovel', 'golden spade', 'gold shovel', 'gold spade'] )
blkdefine(  285, ['golden pick', 'golden pickaxe', 'gold pick', 'golden pickaxe'] )
blkdefine(  286, ['golden axe', 'gold axe'] )
blkdefine(  287, ['string', 'thread', 'spider silk'] )
blkdefine(  288, ['feather'] )
blkdefine(  289, ['sulphur', 'sulfur', 'gunpowder'] )
blkdefine(  290, ['wooden hoe', 'wooden sickle', 'wooden scythe', 'wood hoe', 'wood sickle', 'wood scythe'] )
blkdefine(  291, ['stone hoe', 'stone sickle', 'stone scythe', 'rock hoe', 'rock sickle', 'rock scythe'] )
blkdefine(  292, ['iron hoe', 'iron sickle', 'iron scythe', 'steel hoe', 'steel sickle', 'steel scythe'] )
blkdefine(  293, ['diamond hoe', 'diamond sickle', 'diamond scythe'] )
blkdefine(  294, ['golden hoe', 'golden sickle', 'golden scythe', 'gold hoe', 'gold sickle', 'gold scythe'] )
blkdefine(  295, ['seeds'] )
blkdefine(  296, ['wheat', 'crops'] )
blkdefine(  297, ['bread', 'loaf', 'loaf of bread', 'loafy'] )
blkdefine(  298, ['leather helm', 'leather helmet'] )
blkdefine(  299, ['leather breastplate', 'leather chest piece', 'leather armor', 'leather armour'] )
blkdefine(  300, ['leather greaves', 'leather leggings', 'leather pants'] )
blkdefine(  301, ['leather boots'] )
blkdefine(  302, ['chainmail helm'] )
blkdefine(  303, ['chainmail breastplate'] )
blkdefine(  304, ['chainmail greaves'] )
blkdefine(  305, ['chainmail boots'] )
blkdefine(  306, ['iron helm', 'iron helmet', 'steel helm', 'steel helmet'] )
blkdefine(  307, ['iron breastplate', 'iron chest piece', 'iron armour', 'iron armor', 'steel breastplate', 'steel chest piece', 'steel armour', 'steel armor'] )
blkdefine(  308, ['iron greaves', 'iron leggings', 'iron pants'] )
blkdefine(  309, ['iron boots'] )
blkdefine(  310, ['diamond helm', 'diamond helmet'] )
blkdefine(  311, ['diamond breastplate', 'diamond chest piece', 'diamond armor', 'diamond armour'] )
blkdefine(  312, ['diamond greaves', 'diamond leggings', 'diamond pants'] )
blkdefine(  313, ['diamond boots'] )
blkdefine(  314, ['golden helm', 'golden helmet', 'gold helm', 'gold helmet'] )
blkdefine(  315, ['golden breastplate', 'golden chest piece', 'golden armor', 'golden armour', 'gold breastplate', 'gold chest piece', 'gold armor', 'gold armour'] )
blkdefine(  316, ['golden greaves', 'golden leggings', 'golden pants', 'gold greaves', 'gold leggings', 'gold pants'] )
blkdefine(  317, ['golden boots', 'gold boots'] )
blkdefine(  318, ['flint', 'flint stone', 'fred', 'wilma', 'pebbles'] )
blkdefine(  319, ['raw pork', 'pork belly', 'uncooked pork', 'raw porkchop'] )
blkdefine(  320, ['bacon', 'pork chop', 'cooked pork', 'cooked porkchop', 'cooked pork chop'] )
blkdefine(  321, ['painting', 'canvas', 'art', 'artwork'] )
blkdefine(  322, ['golden apple', 'gold apple'] )
blkdefine(  323, ['sign'] )
blkdefine(  324, ['wooden door', 'wood door'] )
blkdefine(  325, ['bucket', 'iron bucket', 'steel bucket', 'empty bucket'] )
blkdefine(  326, ['bucket of water', 'water bucket'] )
blkdefine(  327, ['bucket of magma', 'magma bucket', 'bucket of lava', 'lava bucket', 'hot sauce'] )
blkdefine(  328, ['minecart', 'cart'] )
blkdefine(  329, ['saddle'] )
blkdefine(  330, ['iron door', 'steel door'] )
blkdefine(  331, ['redstone', 'redstone dust', 'red dust'] )
blkdefine(  332, ['snowball', 'snow ball'] )
blkdefine(  333, ['boat'] )
blkdefine(  334, ['leather'] )
blkdefine(  335, ['milk', 'bucket of milk', 'milk bucket'] )
blkdefine(  336, ['clay brick', 'brick'] )
blkdefine(  337, ['clay ball', 'clay lump', 'lump of clay', 'ball of clay'] )
blkdefine(  338, ['sugar cane', 'reeds', 'bamboo', 'shoots'] )
blkdefine(  339, ['paper', 'page', 'sheet of paper'] )
blkdefine(  340, ['book', 'tome', 'volume'] )
blkdefine(  341, ['slimeball', 'slime ball', 'ball of slime', 'slime'] )
blkdefine(  342, ['storage minecart', 'storage cart'] )
blkdefine(  343, ['powered minecart', 'powered cart'] )
blkdefine(  344, ['egg', 'ovum'] )
blkdefine(  345, ['compass'] )
blkdefine(  346, ['fishing rod', 'fishing pole'] )
blkdefine(  347, ['watch', 'clock', 'timepiece'] )
blkdefine(  348, ['lightstone dust', 'glowstone dust'] )
blkdefine(  349, ['raw fish', 'sushi'] )
blkdefine(  350, ['cooked fish'] )
blkdefine(  351, ['ink sac', 'ink sack', 'dye', 'black dye'] )
blkdefine(  352, ['bone', 'bones'] )
blkdefine(  353, ['sugar', 'lump of sugar'] )
blkdefine(  354, ['cake'] )
blkdefine(  355, ['bed', 'mattress'] )
blkdefine(  356, ['redstone repeater', 'repeater'] )
blkdefine(  357, ['cookie'] )
blkdefine(  358, ['map'] )
blkdefine(  359, ['shears', 'clippers'] )
blkdefine( 2256, ['gold record'] )
blkdefine( 2257, ['green record'] )

