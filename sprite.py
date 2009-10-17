# Copyright (c) 2009, TPSi
# Licensed under BSD license; see LICENSE

# Does a few things: 
#	--	creates CSS classes for icons in icons folder.
#		-- icons should, therefore, be named in CSS class name compatible names
#		-- the CSS classes will be named: icon-iconName
#	--	sprites icons in sets folder into different set files
#		--	stored as a bunch of pngs in folder set-name
#		--	(optional) may have a JSON config.js file with {"repeat": "x", "repeat-width": 32} 
#			or {"repeat":"y", "repeat-height": 32}
#	--	Ones with repeat:x or repeat:y are sprited accordingly (but REQUIRE repeat-width and height). See!

# Sets are folders, containing two or more files;
# At a minimum, they will have a png and a CSS file. Sometimes, however, images are NOT
# sprited (based on size; this can be customized in the set's config file). These images
# will be included separately. The field is max-size, and defaults to 128.

# You run like: python process-images.py (sets folder) (target folder) (optional:url pattern- default: sc_url('images/{0}'))
#	in other words, from this folder: 
#				python process-images.py sets ../resources/images "sc_url('images/{0}')"
# It will create the output directory, if needed.

# The spriting is done in the most simple (and, in some circumstances, inefficient)
# way: by just putting as many icons as can fit in a max-size wide row.

import os, os.path
import sys
import sets

# Defaults. No real purpose... except for the last, which is, in fact, a default
# See, both the first get overriden by the arguments anyway.
sets_directory = "../sets"
target_directory = "../../resources/images"
url_format = "static_url('images/{set}/{image}')"

# parse arguments
a = sys.argv

# There should be at least three...
if len(a) < 3:
	# Whoops! Let's show usage.
	print "Usage:"
	print """python sprite.py <sets folder> <target folder> [url pattern]
Example:
python sprite.py icons/sets resources/images "static_url('images/{set}/{image}')"
Note:
The url pattern is optional, and defaults to the url pattern in the above example.
	"""
	exit()

# Read arguments. Pretty straightforward.
sets_directory = a[1]
target_directory = a[2]
if len(a) > 3:
	url_format = a[3]

# Get the sets we have to deal with
items = os.listdir(sets_directory)

# Prepare a tally
tally = {"plain":0,"sprited":0}
set_count = 0

# Write out header
print ""
print "Set                       Plain        Sprited   "
print "=============================================="

# Loop through items
for i in items:
	# get our path
	path = os.path.join(sets_directory, i)
	
	# No, Python DOES skip "." and ".."... but not .DS_Store, .git, .svn, or any other
	# file hidden through the use of a .-prefix
	# Also, need to skip non-directories.
	if i.startswith(".") or not os.path.isdir(path):
		continue
	
	# process the set
	result = sets.process_set(i, path, os.path.join(target_directory, i), url_format)
	
	# write out info
	print "{set:20} {0[plain]:>10}     {0[sprited]:>10}".format(result, set=i)
	
	# update running total
	tally["plain"] += result["plain"]
	tally["sprited"] += result["sprited"]
	
	# And increment set count
	set_count += 1

# Print footer
print "=============================================="

if set_count > 1:
	plural = "s"
else:
	plural = ""
print "{set:20} {0[plain]:>10}     {0[sprited]:>10}".format(tally, set="Total (" + str(set_count) + " Set" + plural + ")")

if set_count < 1:
	print ""
	print "No sets processed. Did you perhaps pass the set itself, instead of"
	print "the parent sets folder?"
	print ""
	print "Also, if you didn't understand that, read README. It may help."
	print ""