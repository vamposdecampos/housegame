#!/usr/bin/env python

import sys
import whrandom 

class Logger:
	def __init__(self, files = []):
		self.files = files
	def write(self, buf):
		for file in self.files:
			file.write(buf)
	def flush(self):
		for file in self.files:
			file.flush()
	def close(self):
		for file in files:
			file.close()

old_stdout = sys.stdout
sys.stdout = Logger([old_stdout, open("pgenerate.log", "w")])

randrange = whrandom.randrange
print 'seed:', whrandom._inst._seed

prop_names = (
	('Danish', 'Swedish', 'British', 'German', 'Norwegian'),
	('water', 'tea', 'milk', 'coffee', 'beer'),
	('yellow', 'blue', 'red', 'green', 'white'),
	('Dunhill', 'Marlboro', 'Pall Mall', 'Rothmans', 'Winfield'),
	('cat', 'horse', 'bird', 'fish', 'dog'))
verbs = (('the %s', 'is %s'),
	('the one who drinks %s', 'drinks %s'),
	('the one in the %s house', 'lives in the %s house'),
	('the one who smokes %s', 'smokes %s'),
	('the one who has a %s', 'has a %s'))
rule_names = ('', 'RULE_SAME_SLOT', 'RULE_NEXT_TO', 'RULE_LEFT_OF')

RULE_SAME_SLOT = 1
RULE_NEXT_TO   = 2
RULE_LEFT_OF   = 3
RULE_PREDEF    = 4

NUM_SLOTS = len(prop_names)
NUM_PROPS = len(prop_names)
NUM_ITEMS = len(prop_names[0])
props = []
final_map = []
rules = []
dest_map = []
last_force = None

# Init destination map
for k in range(0, NUM_SLOTS):
	dest_map.append([])
	for q in range(0, NUM_PROPS):
		dest_map[k].append(-1)
for k in range(0, NUM_PROPS):
	for q in range(0, NUM_ITEMS):
		while 1:
			slot = randrange(0, NUM_SLOTS)
			if dest_map[slot][k] != -1: continue
			dest_map[slot][k] = q
			break

# Init props & final_map
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
	return None

def add_rule(kind, a="", b=""):
	rules.append([kind, 0, get_id(a), get_id(b)])

def add_predef(slot, name):
	print 'predefined: slot', slot, 'has', name
	(prop, item) = get_id(name)
	for k in range(0, NUM_SLOTS):
		props[k][prop][item] = 0
	for k in range(0, NUM_ITEMS):
		props[slot][prop][k] = 0
	props[slot][prop][item] = 1
	final_map[slot][prop] = item

# Set up a few predefined locations
for k in range(0, 2):
	while 1:
		ok = 1
		slot = randrange(0, NUM_SLOTS)
		prop = randrange(0, NUM_PROPS)
		for (kind, used, (p1, i1), (p2, i2)) in rules:
			if slot == p2: ok = 0
		if ok: break
	add_predef(slot, prop_names[prop][dest_map[slot][prop]])
	rules.append([RULE_PREDEF, 1, (prop, dest_map[slot][prop]), (slot, 0)])

# RULE_SAME_SLOT
for slot in range(0, NUM_SLOTS):
	for prop1 in range(0, NUM_PROPS):
		for prop2 in range(0, NUM_PROPS):
			if prop1 == prop2:
				continue
			rules.append([RULE_SAME_SLOT, 0, (prop1, dest_map[slot][prop1]), (prop2, dest_map[slot][prop2])])

#RULE_LEFT_OF
for slot in range(0, NUM_SLOTS-1):
	for prop1 in range(0, NUM_PROPS):
		for prop2 in range(0, NUM_PROPS):
			rules.append([RULE_LEFT_OF, 0, (prop1, dest_map[slot][prop1]), (prop2, dest_map[slot+1][prop2])])

# RULE_NEXT_TO
for slot in range(0, NUM_SLOTS-1):
	for prop1 in range(0, NUM_PROPS):
		for prop2 in range(0, NUM_PROPS):
			if randrange(0, 100) < 50:
				rules.append([RULE_NEXT_TO, 0, (prop1, dest_map[slot][prop1]), (prop2, dest_map[slot+1][prop2])])
			else:
				rules.append([RULE_NEXT_TO, 0, (prop2, dest_map[slot+1][prop2]), (prop1, dest_map[slot][prop1])])

print len(rules), 'rules generated'

def remove_prop(slot, prop, item, reason=""):
	if not props[slot][prop][item]:
		return 0
	print 'removing', prop_names[prop][item], 'from slot', slot,
	if reason:
		print 'because', reason 
	else:
		print
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
		return 0
	global last_force
	last_force = (prop, item)
	print 'forcing', prop_names[prop][item], 'in slot', slot
	for k in range(0, NUM_SLOTS):
		props[k][prop][item] = 0
	for k in range(0, NUM_ITEMS):
		props[slot][prop][k] = 0
	props[slot][prop][item] = 1
	final_map[slot][prop] = item
	return 1

def is_final(slot, prop, item):
	return final_map[slot][prop] == item

def process_rules():
	changes = 0
	for rule in rules:
		(kind, used, (p1, i1), (p2, i2)) = rule
		if not used: continue

		if kind == RULE_SAME_SLOT:
			for slot in range(0, NUM_SLOTS):
				if not props[slot][p1][i1]:
					changes += remove_prop(slot, p2, i2, 'same_col')
				if not props[slot][p2][i2]:
					changes += remove_prop(slot, p1, i1, 'same_col')
		elif kind == RULE_LEFT_OF:
			remove_prop(NUM_SLOTS-1, p1, i1, 'left_of margin')
			remove_prop(0, p2, i2, 'left_of margin')
			for slot in range(0, NUM_SLOTS-1):
				if not props[slot][p1][i1]:
					changes += remove_prop(slot + 1, p2, i2, 'left_of')
			for slot in range(1, NUM_SLOTS):
				if not props[slot][p2][i2]:
					changes += remove_prop(slot - 1, p1, i1, 'left_of')
		elif kind == RULE_NEXT_TO:
			for slot in range(0, NUM_SLOTS):
				if is_not(slot-1, p1, i1) and is_not(slot+1, p1, i1):
					changes += remove_prop(slot, p2, i2, 'next_to')
				if is_not(slot-1, p2, i2) and is_not(slot+1, p2, i2):
					changes += remove_prop(slot, p1, i1, 'next_to')

	# The only possible item in all slots
	for prop in range(0, NUM_PROPS):
		for item in range(0, NUM_ITEMS):
			count = 0
			for slot in range(0, NUM_SLOTS):
				if props[slot][prop][item]:
					count = count + 1
					sl = slot
			if count == 1:
				changes += force_prop(sl, prop, item)

	# The only item left in one slot
	for slot in range(0, NUM_SLOTS):
		for prop in range(0, NUM_PROPS):
			count = 0
			for item in range(0, NUM_ITEMS):
				if props[slot][prop][item]:
					count = count + 1
					it = item
			if count == 1:
				changes += force_prop(slot, prop, it)

	return changes

def is_finished():
	count = NUM_SLOTS * NUM_PROPS
	for k in range(0, NUM_SLOTS):
		for q in range(0, NUM_PROPS):
			if final_map[k][q] >= 0:
				count = count - 1
	return not count

last_idx = -1
tch = 0
while 1:
	ch = process_rules()
	tch += ch
	if not ch:
		# no changes
		if is_finished(): break
		if last_idx != -1:
			print '*** removing rule', last_idx, 'from ruleset'
			rules[last_idx][1] = 0
		while 1:
			idx = randrange(0, len(rules))
			if rules[idx][1]: continue
			if (rules[idx][0] == RULE_NEXT_TO) and (randrange(0, 100) > 50): continue
			if (rules[idx][0] == RULE_LEFT_OF) and (randrange(0, 100) > 10): continue
			break
		rules[idx][1] = 1
		print '*** adding rule', idx, 'to ruleset:', rules[idx]
		last_idx = idx
	else:
		last_idx = -1

# Dump solution (as if)
print
print 'Solution:'
for k in range(0, NUM_SLOTS):
	for q in range(0, NUM_PROPS):
		if q: print '/',
		print prop_names[q][final_map[k][q]],
	print
print

# Dump compiled rules
for rule in rules:
	(kind, used, (p1, i1), (p2, i2)) = rule
	if not used: continue
	if kind == RULE_PREDEF:
		print "add_predef(%d, '%s')" % (p2, prop_names[p1][i1])
	else:
		print "add_rule(%s, '%s', '%s')" % (rule_names[kind], prop_names[p1][i1], prop_names[p2][i2])
print

# Shuffle
rules = filter(lambda x: x[1], rules)
rules.sort(lambda x, y: randrange(-2, 2))
# List used rules
for rule in rules:
	(kind, used, (p1, i1), (p2, i2)) = rule
	#print rule

	if kind == RULE_SAME_SLOT:
		print verbs[p1][0] % prop_names[p1][i1], verbs[p2][1] % prop_names[p2][i2]
	elif kind == RULE_NEXT_TO:
		print verbs[p1][0] % prop_names[p1][i1], 'lives next to', verbs[p2][0] % prop_names[p2][i2]
	elif kind == RULE_LEFT_OF:
		print verbs[p1][0] % prop_names[p1][i1], 'lives on the left side of', verbs[p2][0] % prop_names[p2][i2]
	elif kind == RULE_PREDEF:
		print verbs[p1][0] % prop_names[p1][i1], 'lives in the', ('1st', '2nd', '3rd', '4th', '5th')[p2], 'house'
print len(rules), 'rules,', tch, 'changes'
(p, i) = last_force
print 'find out where is', verbs[p][0] % prop_names[p][i]

sys.stdout.flush()
