#!/usr/bin/env python

import sys

prop_names = (
	('Danish', 'Swedish', 'British', 'German', 'Norwegian'),
	('water', 'tea', 'milk', 'coffee', 'beer'),
	('yellow', 'blue', 'red', 'green', 'white'),
	('Dunhill', 'Marlboro', 'Pall Mall', 'Rothmans', 'Winfield'),
	('cat', 'horse', 'bird', 'fish', 'dog'))

RULE_SAME_SLOT = 1
RULE_NEXT_TO   = 2
RULE_LEFT_OF   = 3

NUM_SLOTS = len(prop_names)
NUM_PROPS = len(prop_names)
NUM_ITEMS = len(prop_names[0])
props = []
final_map = []
rules = []
for k in range(0, NUM_SLOTS):
	props.append([])
	final_map.append([])
	for q in range(0, NUM_PROPS):
		props[k].append([])
		final_map[k].append(-1)
		for w in range(0, NUM_ITEMS):
			props[k][q].append(1)

def get_id(name):
	for k in range(0, NUM_PROPS):
		for q in range(0, NUM_ITEMS):
			if prop_names[k][q] == name:
				return (k, q)
	assert False, "name %r not found" % name
	return None

def add_rule(kind, a="", b=""):
	rules.append((kind, get_id(a), get_id(b)))

def add_predef(slot, name):
	(prop, item) = get_id(name)
	for k in range(0, NUM_SLOTS):
		props[k][prop][item] = 0
	for k in range(0, NUM_ITEMS):
		props[slot][prop][k] = 0
	props[slot][prop][item] = 1
	final_map[slot][prop] = item

same_col = []
left_of = []
next_to = []

_ = """
add_rule(RULE_SAME_SLOT, 'Danish', 'tea')
add_rule(RULE_SAME_SLOT, 'Pall Mall', 'bird')
add_rule(RULE_SAME_SLOT, 'Dunhill', 'yellow')
add_rule(RULE_SAME_SLOT, 'coffee', 'green')
add_rule(RULE_SAME_SLOT, 'Swedish', 'dog')
add_rule(RULE_LEFT_OF, 'green', 'white')
add_rule(RULE_SAME_SLOT, 'British', 'red')
add_rule(RULE_NEXT_TO, 'horse', 'Dunhill')
add_rule(RULE_NEXT_TO, 'Marlboro', 'cat')
add_predef(2, 'milk')
add_rule(RULE_SAME_SLOT, 'German', 'Rothmans')
add_rule(RULE_SAME_SLOT, 'Winfield', 'beer')
add_rule(RULE_NEXT_TO, 'water', 'Marlboro')
add_rule(RULE_NEXT_TO, 'blue', 'Norwegian')
add_predef(0, 'Norwegian')
"""

add_predef(4, 'bird')
add_predef(1, 'Norwegian')
add_rule(RULE_SAME_SLOT, 'beer', 'Rothmans')
add_rule(RULE_SAME_SLOT, 'green', 'Danish')
add_rule(RULE_SAME_SLOT, 'green', 'dog')
add_rule(RULE_SAME_SLOT, 'Rothmans', 'Danish')
add_rule(RULE_SAME_SLOT, 'Marlboro', 'Norwegian')
add_rule(RULE_SAME_SLOT, 'coffee', 'yellow')
add_rule(RULE_SAME_SLOT, 'coffee', 'horse')
add_rule(RULE_SAME_SLOT, 'yellow', 'Winfield')
add_rule(RULE_SAME_SLOT, 'British', 'Pall Mall')
add_rule(RULE_SAME_SLOT, 'Pall Mall', 'blue')
add_rule(RULE_SAME_SLOT, 'white', 'German')
add_rule(RULE_LEFT_OF, 'milk', 'horse')
add_rule(RULE_LEFT_OF, 'fish', 'bird')
add_rule(RULE_NEXT_TO, 'Swedish', 'water')
add_rule(RULE_NEXT_TO, 'Pall Mall', 'Winfield')
add_rule(RULE_NEXT_TO, 'fish', 'German')


print rules

global done_work
done_work = False

def remove_prop(slot, prop, item, reason=""):
	if not props[slot][prop][item]:
		return 0
	print 'removing', prop_names[prop][item], 'from slot', slot,
	if reason:
		print 'because', reason 
	else:
		print
	global done_work
	done_work = True
	props[slot][prop][item] = 0
	return 1

def draw_map():
	for slot in range(0, NUM_SLOTS):
		for prop in range(0, NUM_PROPS):
			for item in range(0, NUM_ITEMS):
				if props[slot][prop][item]:
					if final_map[slot][prop] == item: ch = '*'
					else: ch = ''
					print ch+prop_names[prop][item],
			print
		print

def is_not(slot, prop, item):
	if slot < 0:
		return 1
	if slot >= NUM_SLOTS:
		return 1
	return not props[slot][prop][item]

def force_prop(slot, prop, item):
	if final_map[slot][prop] == item:
		return
	print 'forcing', prop_names[prop][item], 'in slot', slot
	for k in range(0, NUM_SLOTS):
		props[k][prop][item] = 0
	for k in range(0, NUM_ITEMS):
		props[slot][prop][k] = 0
	props[slot][prop][item] = 1
	final_map[slot][prop] = item
	global done_work
	done_work = True

def is_final(slot, prop, item):
	return final_map[slot][prop] == item

while 1:
	done_work = False

	for rule in rules:
		(kind, (p1, i1), (p2, i2)) = rule
		if kind == RULE_SAME_SLOT:
			for slot in range(0, NUM_SLOTS):
				if not props[slot][p1][i1]:
					remove_prop(slot, p2, i2, 'same_col')
				if not props[slot][p2][i2]:
					remove_prop(slot, p1, i1, 'same_col')
		elif kind == RULE_LEFT_OF:
			remove_prop(NUM_SLOTS-1, p1, i1, 'left_of margin')
			remove_prop(0, p2, i2, 'left_of margin')
			for slot in range(0, NUM_SLOTS-1):
				if not props[slot][p1][i1]:
					remove_prop(slot + 1, p2, i2, 'left_of')
			for slot in range(1, NUM_SLOTS):
				if not props[slot][p2][i2]:
					remove_prop(slot - 1, p1, i1, 'left_of')
		elif kind == RULE_NEXT_TO:
			for slot in range(0, NUM_SLOTS):
				if is_not(slot-1, p1, i1) and is_not(slot+1, p1, i1):
					remove_prop(slot, p2, i2, 'next_to')
				if is_not(slot-1, p2, i2) and is_not(slot+1, p2, i2):
					remove_prop(slot, p1, i1, 'next_to')

	# The only possible item in all slots
	for prop in range(0, NUM_PROPS):
		for item in range(0, NUM_ITEMS):
			count = 0
			for slot in range(0, NUM_SLOTS):
				if props[slot][prop][item]:
					count = count + 1
					sl = slot
			if count == 1:
				force_prop(sl, prop, item)

	# The only item left in one slot
	for slot in range(0, NUM_SLOTS):
		for prop in range(0, NUM_PROPS):
			count = 0
			for item in range(0, NUM_ITEMS):
				if props[slot][prop][item]:
					count = count + 1
					it = item
			if count == 1:
				force_prop(slot, prop, it)

	count = NUM_SLOTS * NUM_PROPS
	for k in range(0, NUM_SLOTS):
		for q in range(0, NUM_PROPS):
			if final_map[k][q] >= 0:
				count = count - 1
	if not count:
		break
	if not done_work:
		print "can't work any further, dumping partial map."
		print
		draw_map()
		sys.exit(1)

	#print
	#draw_map()
	#sys.stdin.read(1)

print
print 'Solution:'
for k in range(0, NUM_SLOTS):
	for q in range(0, NUM_PROPS):
		if q: print '/',
		print prop_names[q][final_map[k][q]],
	print
