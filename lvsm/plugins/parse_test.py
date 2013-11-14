import ldparser
import kaparser
import sys

if len(sys.argv) != 2:
	print "Need config file name"
	sys.exit(0)
	
c = sys.argv[1]

f = open(c)
conf = "".join(f.readlines())

#t = ldparser.tokenize_config(conf)
t = kaparser.tokenize_config(conf)

if t:
	print "%s parsed OK!" % c
	print t.dump()
	# for i in t:
		# print i
else:
	print "%s didn't parse OK!" % c
