# Copyright (c) 2009, TPSi
# Licensed under BSD license; see LICENSE

# These are standard python...
import os, os.path, shutil

# And for this you need PIL
import Image

# and for this, you need either Python 2.6+, which has built-in JSON,
# or simplejson
try:
	import simplejson as josn
except ImportError:
	import json

# process_set: 	processes a set folder. set_name supplied for errors and CSS
def process_set(set_name, set_path, output_set_path, url_form):
	# Check that the input set exists.
	if not os.path.exists(set_path):
		print "Could not process set ", set_name, "; input not found."
		print "Note: since scanning occurs automatically, this should not happen,"
		print "and as such, is a bug. Please report."
	
	# Make the output set if needed
	if not os.path.exists(output_set_path):
		os.makedirs(output_set_path)
	
	# Need to know if there is a config file
	# First, prepare default config.
	config = {
		"max-size": 128,
		"repeat": "none",
		"repeat-width": 32,
		"repeat-height": 32
	}
	
	# Now, load actual config if necessary, mixing in to default
	config_path = os.path.join(set_path, "config.json")
	if os.path.exists(config_path):
		try:
			config_file = open(config_path)
			config.update(json.loads(config_file.read()))
		except:
			print "Could not load config file. Proceeding anyway. What's the worst tha"
	
	# Loaded config. 
	# So... time to get a list of pngs and jpegs.
	raw_items = os.listdir(set_path)
	items = []
	for item in raw_items:
		# if NOT a jpg or png, well... we can't really do anything with it, can we?
		if not item.endswith(".jpg") and not item.endswith(".png"):
			continue
		
		# Otherwise, we are in luck: add to the item set!
		items.append(item)
	
	# Now that we have images to use,we need to get their sizes so we can calculate a
	# layout plan. We just create a new set of images.
	images = []
	for item in items:
		path = os.path.join(set_path, item)
		img = Image.open(path)
		
		image_info = {
			"name": os.path.splitext(item)[0],
			"path": path,
			"size": img.size
		}
		images.append(image_info)
	
	# Sort by size, in reverse.
	# Why? Because putting all the large ones in one place should make things a bit
	# more organized, I would think.
	images.sort(lambda a, b: cmp(a["size"][0], b["size"][0]), reverse=True)
	
	# Calculate plan
	sprite_width = 0	# Current calculated width of the final image. max-size unless in a repeat mode
	sprite_height = 0	# Current calculated height of the final image. Usually calculated, unless in repeat-y
	cx = 0				# X position for the next sprite
	cy = 0				# Y position for the next sprite
	ch = 0				# height of the current row.
	
	plain = []			# Images which are NOT being sprited for one reason or another (usually too large)
	sprites = []		# Images which ARE being sprited.
	for image in images:
		# Do things differently in a repeat mode
		if config["repeat"] == "x":
			# Lay it out, but instead of the normal algorithm, just arrange in rows.
			sprite = {
				"x": cx, # should always 0
				"y": cy, # should increment each time
				"width": config["repeat-width"],
				"height": image["size"][1],
				"name": image["name"],
				"path": image["path"],
				"url": url_form.format(set=set_name, image="sprites.png"),
				"repeat": "repeat-x"
			}
			
			sprite_width = config["repeat-width"]
			cy += image["size"][1]
			sprite_height = cy
			sprites.append(sprite)
			continue
			
		elif config["repeat"] == "y":
			# Similar to above, but arranges in columns.
			sprite = {
				"x": cx, # always 0 here
				"y": cy,
				"width": image["size"][0],
				"height": config["repeat-height"],
				"name": image["name"],
				"path": image["path"],
				"url": url_form.format(set=set_name, image="sprites.png"),
				"repeat": "repeat-y"
			}
			
			sprite_height = config["repeat-height"]
			cx += image["size"][0]
			sprite_width = cx
			sprites.append(sprite)
			continue
		
		# First, leave alone images larger than max-size. Yes, even for repeat.
		if image["size"][0] > config["max-size"] or image["size"][1] > config["max-size"]:
			# add to plain set
			target = os.path.join(output_set_path, image["name"] + ".png")
			plain.append({
				"width": image["size"][0],
				"height": image["size"][1],
				"name": image["name"],
				"path": image["path"],
				"target": target,
				"url": url_form.format(set=set_name, image=image["name"] + ".png")
			})
			
			# and copy file
			shutil.copy2(image["path"], target)
			
			continue
			
		
		# Move to next row if needed
		if cx + image["size"][1] > config["max-size"]:
			# IT IS NEEDED! OH NOES!
			cx = 0
			cy += ch
			ch = 0
		
		# Move now
		sprite = {
			"x": cx,
			"y": cy,
			"width": image["size"][0],
			"height": image["size"][1],
			"name": image["name"],
			"path": image["path"],
			"repeat": "no-repeat",
			"url": url_form.format(set=set_name, image="sprites.png")
		}
		
		# add to row
		sprites.append(sprite)
		cx += image["size"][0]
		ch = max(ch, image["size"][1])
		
		# update sprite width and height
		sprite_width = max(sprite_width, cx)
		sprite_height = max(sprite_height, cy + ch)
	
	# allocate image and prepare a CSS string
	css = ""
	gen = Image.new("RGBA", (sprite_width, sprite_height), (0, 0, 0, 0))
	
	# Start generating
	for sprite in sprites:
		img = Image.open(sprite["path"])
		gen.paste(img, (sprite["x"], sprite["y"]))
		
		# Create some CSS
		css += ".{setName} .{className}.icon, .{setName}.{className}.icon {{ background:{url} {repeat}; background-position:-{x!s}px -{y!s}px; }}\n".format(
			setName=set_name,
			className=sprite["name"], 
			width=sprite['width'],
			height=sprite['height'],
			x=sprite['x'], 
			y=sprite['y'],
			repeat=sprite["repeat"],
			url=sprite["url"]
		)
	
	# Save image... if there is anything to save
	if len(sprites) > 0:
		gen.save(os.path.join(output_set_path, "sprites.png"), "PNG")
	
	# now, prepare non-sprite CSS
	for image in plain:
		css += ".{setName} .{className}.icon, .{setName}.{className}.icon {{ background:{url}; }}\n".format(
			setName=set_name,
			className=image["name"],
			width=image["width"],
			height=image["height"],
			url=image["url"]
		)
	
	css_file = open(os.path.join(output_set_path, "images.css"), "w")
	css_file.write(css)
	css_file.close()
	
	# Return statistics
	return {
		"plain": len(plain),
		"sprited": len(sprites)
	}























