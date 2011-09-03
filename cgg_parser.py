"""cgg comiler
Version: 1.0
Author: onesuper
E-mail: onesuperclark@gmail.com



This module is the main part of the compiler which provides
both syntax and semantics proccessing during the compilation.

It is a recursive decent parser for a simple syntax called PL/0.
The parser also generates the object code according to the semantics.

"""

import sys
import cgg_lex as l

"""Global variables are defined as follow:

'pointer' is the index of the sentence which is imported
from the lexical analysis module. Call the method getSen()
to set it up.

NOTE:
Dictionary has the global scope in Python, but the ordinary 
variable has not. In order to access "sentence" in the scope
of function, key word "global" is used.  
"""
sentence = []
pointer = 0
has_error = False
cutoff = False  # set to cutoff the debug function

symbol_table = {}
quate_list = []
output_fp = None
used_temp_index = 0 # T0, T1, T2, T3 ...
output_line_no = 1
saved_line = 1  # to go to line in while-loop
refill_line = 1
"""Some semantic actions are defined as function as follow:
"""
def match(symName):
	"""
	1.match the symbol just read in
	2.print the successful message
	3.the output information can be sealed when
	  cutoff = True
	"""
	global pointer
	global cutoff
	pointer += 1
	if cutoff == False:
		print "match " + symName + " and the pointer is moving to %s" % sentence[pointer][0]

def during(funcName):
	global pointer
	global cutoff
	if cutoff == False:
		print "during " + funcName + " and the pointer is on %s" % sentence[pointer][0]

def error(info):
	global has_error
	has_error = True
	print "SyntaxError: " + info
	sys.exit()

def getSym():
	global pointer
	return sentence[pointer][0] 

def getVal():
	global pointer
	return sentence[pointer][1]

# get the whole sentence from the source file
def getSen():
	global sentence
	sentence = l.resList
	sentence.append(("EOF", None))  # to prevent the match() out of index 

def append(name, value):
	symbol_table[name] = value
	return 

# return the index in the sybol table of the given name
def entry(name):
	return name

def openOut():
	global output_fp
	output_fp = open("test.out", 'w')

def closeOut():
	global output_fp
	output_fp.close()

def save_point():
	global output_line_no
	global saved_line
	saved_line = output_line_no

def getSavedPoint():
	global saved_line
	return saved_line

def save_refill():
	global output_line_no
	global refill_line
	refill_line = output_line_no

def refill():
	global output_line_no
	global refill_line
	temp = quate_list[refill_line-1]
	quate_list[refill_line-1] = (temp[0], temp[1], temp[2], temp[3], output_line_no)  

# always give a new temp name, e.g. T0, T1, T2
# and append to the symbol_table
# finally, return the index in the symbol_table
def newTemp():
	global used_temp_index
	used_temp_index += 1
	name = '#TEMP' + str(used_temp_index) # give a unique name to the temporary variable
	append(name, None)
	return name

def gen(op, arg1, arg2, result):
	global output_line_no
	quate_list.append((output_line_no, op, arg1, arg2, result))
	output_line_no += 1

def gen2(op, arg1, arg2, offset):
	global output_line_no
	jump_to = output_line_no + offset
	quate_list.append((output_line_no, op, arg1, arg2, jump_to))
	output_line_no += 1

def outPutQuate():
	for line in quate_list:
		output_fp.write(str(line[0])+ ": (" + str(line[1]) + ", "+ str(line[2]) + ", " + str(line[3]) + ", " + str(line[4]) + ")\n")

"""
Each function corresponds to a non-terminal in PL/0 grammar

the EBNF description of PL/0 language is:

	program	= block "."

	block	= [ CONST "ident" = "number" { "," ident "=" "number" } ";" ]
			  [ VAR "ident" { "," "ident" ";"}
			  { PROCEDURE "ident" ";" block ";"}
			  statement
	
	statement = [ CALL "ident" |
				  BEGIN statement { ";" statement } END |
				  IF condition THEN statement |
				  WHILE condition DO statement |
				  "ident" ":=" expresssion ]
	
	condition = ODD expression | 
				expression ( "=" | "#" | "<" | "<=" | ">" | ">=" ) expression

	expression = [ "+" | "-" ] term { ( "+" | "-" ) term }

	term = factor { ( "*" | "/") factor }

	factor = "ident" | "number" | "(" expression ")"
"""

def program():
	during("program()")
	block()
	if getSym() == ".":
		# match(".")   
		print "match . and can not move any farther."
		print "The compilation is finished!"
		return
	else:
		error("missing '.' at the end of the program.")
		

def block():
	during("block()")

	# constants difinition area
	if getSym() == "CONST":
		match("CONST")
		if getSym() == "ident":
			id = getVal()
			match("ident")
			if getSym() == "=":
				match("=")
				if getSym() == "const":
					val = getVal()
					match("const")
					append(id, val) # append in the dict
				else:
					error("missing number after the alignment symbol '='.")
				while getSym() == ",":
					match(",")
					if getSym() == "ident":
						id = getVal()
						match("ident")
						if getSym() == "=":
							match("=")
							if getSym() == "const":
								val = getVal()
								match("const")
								append(id, val) # append in the dict
							else:
								error("missing number after the alignment symbol '='.")
						else:
							error("missing '=' in the CONST declaration.")
				if getSym() == ";":	
					match(";")
				else:
					error("don't forget ';' after CONST declaration.")
			else:
				error("missing '=' in the CONST declaration.")
		else:
			error("missing identifier in the CONST declaration.")
	
	# variables difinition area
	if getSym() == "VAR":
		match("VAR")
		if getSym() == "ident":
			id = getVal()
			match("ident")
			append(id, 0) # append in the symbol table
			while getSym() == ",":
				match(",")
				if getSym() == "ident":
					id = getVal()
					match("ident")
					append(id, 0) # append in the symbol table
				else:
					error("missing identifier in the VAR declaration.")
			if getSym() == ";":
				match(";")
			else:
				error("don't forget ';' after the VAR declaration.")
		else:
			error("missiong identifier in the VAR declaration.")

	
	# PROCEDURE definition area:
	while getSym() == "PROCEDURE":
		match("PROCEDURE")
		if getSym() == "ident":
			match("ident")
			if getSym() == ";":
				match(";")
				block()
				if getSym() == ";":
					match(";")
				else:
					error("missing ';' after the PROCEDURE body.")
			else:
				error("don't forget ';' after PROCEEDURE declaration.")
		else:
			error("missing identifier when defining the PROCEDURE.")
	
	# statement area
	statement()
	return


def statement():
	during("statement()")

	# CALL procedure
	if getSym() == "CALL":
		match("CALL")
		if getSym() == "ident":
			match("ident")
			return
		else:
			error("missing identifier after 'CALL'.")
	
	# BEGIN...END
	if getSym() == "BEGIN":
		match("BEGIN")
		statement()

		while getSym() == ";":
			match(";")
			statement()

		if getSym() == "END":
			match("END")
			return 
		else:
			error("missing 'END' in 'BEGIN...END' statement.")
	
	# IF...THEN... 
	if getSym() == "IF":
		match("IF")
		condition()
		if getSym() == "THEN":
			match("THEN")
			statement()
			return
		else:
			error("missing 'THEN' in 'IF...THEN' statement.")
	
	# WHILE...DO...
	if getSym() == "WHILE":
		match("WHILE")
		save_point()   # save the condition positon, then you can come back to it
		place1 = condition()  # got the result of condition:true/false
		save_refill() # remember this line, we will refill the 0 with the last line of while...do
		gen("je", place1, "_", "0") # get out of the while...do
		if getSym() == "DO":
			match("DO")
			statement()
			# in the end of loop, jump back to the condtion
			gen("jmp", '_', '_', getSavedPoint())
			refill()  # we will refill here
			return
		else:
			error("missing 'DO' in 'WHILE...DO' statement.")
	
	# at leat one assignment statement in the statement
	if getSym() == "ident":
		i = getVal()
		match("ident")
		if getSym() == ":=":
			match(":=")
			place = expression()
			gen(":=", place, "_", entry(i)) # gen!!!
			return
		else:
			error("missing the alignment symbol")
	
	# could be nothing
	return
		


def condition():
	during("condition()")
	if getSym() == "ODD":
		match("ODD")
		expression()
		return
	else:
		place1 = expression()
		if getSym() == "=":
			op = getSym()
			match("=")
		elif getSym() == "#":
			op = getSym()
			match("#")
		elif getSym() == "<":
			op = getSym()
			match("<")
		elif getSym() == "<=":
			op = getSym()
			match("<=")
		elif getSym() == ">":
			op = getSym()
			match(">")
		elif getSym() == ">=":
			op = getSym()
			match(">=")
		else:
			error("missing the operation('=', '#', '<', '<=', '>', '>=') in the expression")
		place2 = expression()
		place = newTemp()
		gen2(op, place1, place2, 3)  # nextstart + 3
		gen(":=", 0, "_", place)
		gen2("jmp", "_", "_", 2)   # nextstart + 2
		gen(":=", 1, "_", place)
		return place

def expression():
	during("expression()")
	if getSym() == "+" or getSym() == "-":
		if getSym() == "+":
			match("+")
			place1 = term()
			while getSym() == "+" or getSym() == "-":
				if getSym() == "+":
					match("+")
					place2 = term()
					place = newTemp()
					gen('+', place1, place2, place)
					return place
				else:			 # imply getSym() == "-"
					match("-")
					place2 = term()
					place = newTemp()
					gen('+', place1, place2, place)
					return place
			else:
				return place1
		else:   #imply getSym() == "-"  @ means get the -x of x
			match("-")
			place1 = term()
			while getSym() == "+" or getSym() == "-":
				if getSym() == "+":
					match("+")
					place2 = term()
					place = newTemp()
					gen('+', place1, place2, place)
					place_new = newTemp()
					gen('@', place, '_', place_new)
					return place_new
				else:			 # imply getSym() == "-"
					match("-")
					place2 = term()
					place = newTemp()
					gen('-', place1, place2, place)
					place_new = newTemp()
					gen('@', place, '_', place_new)
					return place_new
			else:
				return place1
	else:  # not starting with "+"/"-"
		place1 = term()
		while getSym() == "+" or getSym() == "-":
			if getSym() == "+":
				match("+")
				place2 = term()
				place = newTemp()
				gen('+', place1, place2, place)
				return place
			else:			 # imply getSym() == "-"
				match("-")
				place2 = term()
				place = newTemp()
				gen('-', place1, place2, place)
				return place
		return place1



def term():
	during("term()")
	place1 = factor()
	while getSym() == "*" or getSym() == "/":
		if getSym() == "*":
			match("*")
			place2 = factor()
			place = newTemp()
			gen('*', place1, place2, place)  #gen!!!!!!!!!
			return place
		else:			# imply getSym() == "/"
			match("/")
			place2 = factor()
			place = newTemp()
			gen('/', place1, place2, place)
			return place
	else:
		return place1



def factor():
	during("factor()")
	if getSym() == "ident":
		place = entry(getVal())  # use getVal here!
		match("ident")
		return place
	elif getSym() == "const":
		place = entry(getVal())
		match("const")
		return place
	elif getSym() == "(":
		match("(")
		place = expression()
		if getSym() == ")":
			match(")")
			return place     # do not gen, but return
		else:
			error("missing left parentthesis(')') in this sentence")
	else:
		error("syntax error in the factor.")
