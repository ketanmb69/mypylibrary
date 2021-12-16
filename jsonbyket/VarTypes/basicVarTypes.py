import argparse, shlex, sys
class prompt:
	def __init__(self, jbk):
		self.jbk = jbk
		self.name = "prompt" 
	def get_value(self, rule, value=''):
		pText = value.split("$prompt ")[1]
		return input(pText)

class arg:
	def __init__(self, jbk):
		self.jbk = jbk
		self.name = "arg" 
	def get_value(self, rule, value=''): 
		name = value.split("$arg ")[1]
		value = None
		for x, i in zip(sys.argv, range(len(sys.argv))):
			if x == name:
				value = sys.argv[i+1]
				break
		return value