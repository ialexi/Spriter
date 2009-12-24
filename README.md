Usage
===============================================================================
Running without arguments will show usage:
	python sprite.py

The usage is as follows:
	python sprite.py <sets folder> <target folder> [url pattern]

Example:
	python sprite.py icons/sets resources/images "static_url('images/{set}/{image}')"

Running Provided Example (from this folder, containing sprite.py):
	python sprite.py example-sets example-output

**Note:**
The url pattern is optional, and defaults to the url pattern in the above example.


Mild Warning
===============================================================================
Spriter WILL overwrite files it sees. You only have to worry about this if you
have:
	<target folder>/(a set name)/images.css
	<target folder>/(a set name)/sprites.png
	<target folder>/(a set name)/(name of an unspritable image)

So, not much danger... but there is a danger.


Requirements
===============================================================================
The script is written in Python. It requires:

- Either: Python 2.6+ or Python 2.5 with simplejson installed
- PIL (Python Imaging Library)

What it does:
===============================================================================
- Takes a “sets” folder, which should have sub-folder “sets” of icons to 
  be sprited.

- Takes an output folder, under which it will create new set folders 
  containing CSS and image files.

- Combines images under a maximum size (128x128 by default—see 
  Configuration) into a sprites.png file in the output set folder.
		
- Creates CSS referencing these images using a URL template (SproutCore 
  oriented by default—see URLs)

Sets
===============================================================================
You may often have more than one set of icons. For instance, you could have a 
main set and an alternate set that you only want to load on demand, and still 
want that additional set to be sprited. 

Alternatively, you may have images meant for repeating backgrounds, but which
should still be sprited.

To facilitate this, the spriting script takes, as its first argument, the location of
a sets folder. You put your sets as subfolders into this folder. For instance, this could be your layout:

	my-sets
		common
			delete-32.png
			delete-64.png
			file-32.png
			file-64.png
			upload.png
		repeat-x
			config.js       — see Configuration
			toolbar.png
			footer.png
			header.png
		odd-feature
			some-icon.png
			other-icon.png

URLs
===============================================================================
The CSS has to reference the images. Only problem: it doesn’t know where those 
images are.

Usually, you’d just be able to use paths relative to the stylesheet. However, 
if you are using SproutCore, this won’t work because it moves around all the CSS
and JavaScript.

Without SproutCore, you'd need: url('sprites.png')
With SproutCore, you need something more like: static_url(‘images/set/sprites.png’)

By default, the script structures it for SproutCore, just like above. It uses a URL 
template of "static_url('images/{set}/{image}')". You can easily change this by
changing the third argument for the script.


Configuration
===============================================================================
There are a few things that are configurable. Configuration is done per-set.

Configuration files are JSON files, and are very simple. They are optional, and 
take at most five parameters:

-	prepend-set-name: default: True. 
	Determines whether to prepend the set name onto the CSS class. If
	false, the CSS class will simply be the name of the image (not including
	extension). 

-	max-size: default: 128. 
	The maximum size for sprited images. Images above this size will be put 
	as separate images. Useful if you have some really high-res icons you 
	don’t want to sprite, but want to keep with the set.

-	repeat: Default: “none”; can also be “x” or “y”. 
	Determines the repeat mode. If repeat is “x,” the sprites will be laid
	out in rows; if “y,” the sprites will be laid out in columns. The generated
	CSS will include repeat-x or repeat-y, respectively.  Note 	that all 
	images in a repeat-x set must be the same width, and all images in a 
	repeat-y set must be the same height. The width or height of these images
	should be set using repeat-width and repeat height, which are discussed below. 

-	repeat-width: Default: 32. If repeat=“x,” the width of the repeat images. 
	If your repetition does not require a pattern, you could set this to 1. 

-	repeat-height: See that lovely summary of repeat-width above? Well, 
	this is the same, but for y/height.

Where do the config files go? In the set folder, named config.json.

Nice and simple, eh?