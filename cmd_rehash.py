# coding=UTF-8
import traceback
import inspect
import sys
import gc

# Find any objects tracked by the garbage collector which have a
# __module__ attribute with the same module name being rehashed.
# The list will include all of the module's class definitions, and
# all instances of said classes (instances inherit __module__ from
# their classes).
def get_objects( name ):
	return [ x for x in gc.get_objects() if getattr( x, "__module__", None ) == name ]

def do_rehash( reply, name ):
	# Perform absolute import in case this is a brand new module
	__import__( name, level = 0 )

	# When importing a submodule of the form X.Y, __import__ will only
	# return the top-level X. The submodule Y that was actually imported
	# can be found in the sys.modules dictionary.
	module = sys.modules[ name ]

	# Build a set with just the module's class definitions. This will
	# find global classes, nested classes, and even classes that were
	# created at runtime inside a function.
	objects = get_objects( name )
	old_classes = set(( x for x in objects if inspect.isclass(x) ))

	# Reload the module, and find all the classes defined in the new
	# version of the module. Because __module__ is a string, it will match
	# for both old and new versions of the same class. An additional check
	# is needed against old_classes to eliminate the old versions. The full
	# list "objects" is used later to find all class instances that need
	# a class transplant.
	module = reload( module )
	objects = get_objects( name )
	classes = ( x for x in objects if inspect.isclass(x) and not x in old_classes )

	# Build a dictionary mapping the class name to the class object for
	# all the classes defined in the new version of the module. Also find
	# classes with a duplicate name, since these cannot be safely
	# transplated into existing objects.
	new_classes = {}
	dup_classes = set()
	for cls in classes:
		name = cls.__name__
		if name in new_classes:
			dup_classes.add( name )
		new_classes[ name ] = cls

	# For each class defined in the old module, find all objects tracked
	# by the garbage collector which are instances of said class. If a new
	# class definition can be found which has the same __name__ as the old,
	# then update the __class__ of the instance object to point at the new
	# class. Any old classes that cannot be matched to a unique new class
	# and any classes that cause an exception during transplant (e.g. mixing
	# old and new style classes) are flagged as errors and reported later
	# via reply.say().
	err_classes = set()
	for obj in objects:
		try:
			if getattr(obj, "__class__", None) in old_classes:
				name = obj.__class__.__name__
				if name in new_classes and not name in dup_classes:
					try:
						obj.__class__ = new_classes[ name ]
					except:
						traceback.print_exc()
						err_classes.add( name )
				else:
					err_classes.add( name )
					if name in dup_classes:
						print 'Duplicate class "%s" on %s' % \
							(name, repr(obj))
					else:
						print 'Missing class "%s" on %s' % \
							(name, repr(obj))
		except:
			traceback.print_exc()

##	  for cls in old_classes:
##		  for obj in gc.get_referrers( cls ):
##			  if isinstance( obj, cls ):
##				  try:
##					  name = cls.__name__
##					  if name in new_classes and not name in dup_classes:
##						  obj.__class__ = new_classes[ name ]
##					  else:
##						  err_classes.add( name )
##						  if name in dup_classes:
##							  print 'Duplicate class "%s" on %s' % \
##								  (name, repr(obj))
##						  else:
##							  print 'Missing class "%s" on %s' % \
##								  (name, repr(obj))
##				  except:
##					  traceback.print_exc()

	# Report an error summary back to IRC or Minecraft
	if err_classes:
		reply.say( "[!] Could not transplant classes: " + ", ".join(err_classes) )
