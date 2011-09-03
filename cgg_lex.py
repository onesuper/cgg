"""
Version: 1.0
Author: onesuper
E-mail: onesuperclark@gmail.com

This modelue providing a function(getWord()) to get a symbol from 
the source code each time it is called in the parser module. 
"""


import os
import string
import sys
import re


"""
Reserved Words are defined here:

DON'T ALTER THE FOLLOWING TABLES, unless you HAVE TO
change the language itself. 

The dictionary maps the reserved kewords/symbols(which
appear in the source code) to the internal types of 
the program, in this case, String.
""" 
kwordDict = {
		"PROGRAM"	: "PROGRAM",
		"PROCEDURE" : "PROCEDURE",
		"CALL"		: "CALL",
		"BEGIN"		: "BEGIN",
		"END"		: "END",
		"CONST"		: "CONST",
		"VAR"		: "VAR",
		"WHILE"		: "WHILE",
		"DO"		: "DO",
		"IF"		: "IF",
		"THEN"		: "THEN"
		}

symDict = {
		"+"		: "+",
		"-"		: "-",
		"*"		: "*",
		"/"		: "/",
		":="	: ":=",
		"="		: "=",
		"#"		: "#",
		">"		: ">",
		">="	: ">=",
		"<"		: "<",
		"<="	: "<=",
		"("		: "(",
		")"		: ")",
		";"		: ";",
		","		: ",",
		"."		: "."
		}


"""The internal representation of source code is like thus:

[ "VAR x, y",
  "PROCEDURE ",
  "\tBEGIN",
  "\t\tx:=x+1",
  ...
  ]

"""


srcList = []



"""The result of lexical analysis is kept in a list

LIKE:

[ ("VAR", None),
  ("ident", "x"),
  (",", None)
  ...
  ]

"""
resList = []


def getSrc(srcPath):
	global srcList
	"""read the source code on the disk
	and convert it to a List
	"""
	srcFile = open(srcPath, "r")
	srcList = srcFile.readlines()
	srcFile.close()

def getRes():
	srcLen = len(srcList)
	lineNo = 0
	buf = ""
	bufLen = 0
	now = 0 # a cursor in the buf
	errorFlag = False
	strToken = ""
	while True:
		if lineNo == srcLen:  #out of the source code
			break
		line = srcList[lineNo]
		lineNo += 1
		if errorFlag == True:
			break
		line = line.strip() #strip the white space
		if line == "":
			continue #skip the empty line
		buf += line
		now = 0
		bufLen = len(buf)
		while now < bufLen:
			#eat the blank
			if buf[now] == " ":
				now += 1
			#ident or keyword
			elif IsLetter(buf[now]):
				strToken += buf[now]
				now += 1
				#maybe it has already rushed out of buffer
				if now == bufLen:
					if kwordDict.has_key(strToken):
						resList.append((kwordDict[strToken], None))
					else:
						resList.append(("ident", strToken))
				else:
					while IsLetter(buf[now]) or IsDigit(buf[now]):
						strToken += buf[now]
						now += 1
						if now >= bufLen:
							break	#in case the cursor out of the buf
					#judge if it is a keyword
					if kwordDict.has_key(strToken):
						resList.append((kwordDict[strToken], None))
					else:#it is an identifier
						resList.append(("ident", strToken))
				strToken = "" #clear up the token after being recognized
			#number constant
			elif IsDigit(buf[now]):
				strToken += buf[now]
				now += 1
				#maybe it has already rushed out of buffer
				if now == bufLen:
					resList.append(("const", string.atoi(strToken)))
				else:
					while IsDigit(buf[now]):
						strToken += buf[now]
						now += 1
						if now >= bufLen:
							break  #in case the cursor out og the buf
					resList.append(("const", string.atoi(strToken)))
				strToken =""
			#symbol
			elif buf[now] == ":":   #since
				now += 1
				if buf[now] == "=":
					resList.append((symDict[":="], None))
					now += 1
				else:
					print "LexicalError(%d): missing '=' after ':'" % lineNo
					errorFlag = True
			elif buf[now] == "+":
				resList.append((symDict["+"], None))
				now += 1
			elif buf[now] == "-":
				resList.append((symDict["-"], None))
				now += 1
			elif buf[now] == "*":
				resList.append((symDict["*"], None))
				now += 1
			elif buf[now] == "/":
				resList.append((symDict["/"], None))
				now += 1
			elif buf[now] == "=":
				resList.append((symDict["="], None))
				now += 1
			elif buf[now] == "#":
				resList.append((symDict["#"], None))
				now += 1
			elif buf[now] == ">":
				if now == bufLen - 1: # ">" is at the end of buf
					resList.append((symDict[">", None]))
					now += 1
				else:
					if buf[now+1] == "=":
						resList.append((symDict[">="], None))
						now += 2
					else:
						resList.append((symDict[">"], None))
						now += 1
			elif buf[now] == "<":
				if now == bufLen - 1: # ">" is at the end of buf
					resList.append((symDict["<", None]))
					now += 1
				else:
					if buf[now+1] == "=":
						resList.append((symDict["<="], None))
						now += 2
					else:
						resList.append((symDict["<"], None))
						now += 1
			elif buf[now] == "(":
				resList.append((symDict["("], None))
				now += 1
			elif buf[now] == ")":
				resList.append((symDict[")"], None))
				now += 1
			elif buf[now] == ";":
				resList.append((symDict[";"], None))
				now += 1
			elif buf[now] == ",":
				resList.append((symDict[","], None))
				now += 1
			elif buf[now] == ".":
				resList.append((symDict["."], None))
				now += 1
			else:
				print "Lexical Error(%d):" % lineNo
				error_flag = True
				break
		now = 0		#reset the cursor to the head of buffer
		buf = ""	#release the buf


def IsLetter(ch):
	if re.match(r'[a-zA-Z]', ch):
		return True
	else:
		return False

def IsDigit(ch):
	return ch.isdigit()

