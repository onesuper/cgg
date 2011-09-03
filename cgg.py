"""cgg compiler
Version: 1.0
Author: onesuper
Email: onesuperclark@gmail.com


This is the driver of the compiler.
"""

import sys
import os
import cgg_parser as p
import cgg_lex as l


if __name__ == "__main__":

	if len(sys.argv) < 2:
		print "please give the name of source file!"
		sys.exit()

	srcPath = os.getcwd()
	srcPath += os.sep
	srcPath += sys.argv[1]
	
	# get
	l.getSrc(srcPath)
	
	#start the lexical analyzer
	l.getRes()

	print l.resList
	
	# send information
	p.getSen()

	print p.sentence

	#start the syntax analyzer
	p.openOut() 
	p.program()

	print p.symbol_table
	print p.quate_list
	p.outPutQuate()
	p.closeOut()


