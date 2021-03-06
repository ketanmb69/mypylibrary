from ..utils import seperate_string_number
import math
from ..jsonbyket import jsonbyket

class DataType:
	def __init__(self, jbk:jsonbyket):
		self.jbk = jbk
		#name, t, and default all need to be set.
		self.name = "none"
		self.t = None
		self.default = None
	#returns true/false, whether or not the data is this type
	def matches(self, data):
		if type(data) == self.t:
			return True
		return False
	#data - the data provided from the config file. rule - the rules for this property.
	def convert(self, data, ruleset, parentUID="ROOT"):
		if type(data) != self.t:
			raise Exception("Invalid type!")
		return data



class string(DataType):
	def __init__(self, jbk):
		super().__init__(jbk)
		self.name = "string"
		self.t = str
		self.default = ""
	
	def convert(self, data, rule, parentUID="ROOT"): #strings have no rules YET (todo: add min/max length)
		return str(data)

class number(DataType):
	def __init__(self, jbk):
		super().__init__(jbk)
		self.name = "number"
		self.t = float
		self.default = 0
	#returns true/false, whether or not the data is this type
	def matches(self, data):
		newData = data
		try:
			newData = float(data)
		except:
			return False
		return type(newData) == float or type(newData) == int
	
	def convert(self, data, rule, parentUID="ROOT"):
		value = float(data)
		minval = self.jbk.get_property(rule, "min", parentUID, noneFound=-math.inf)
		maxval = self.jbk.get_property(rule, "max", parentUID, noneFound=math.inf)
		multiplier = float(self.jbk.get_property(rule, "multiplier", parentUID, noneFound=1))
		value *= multiplier
		isInt = self.jbk.get_property(rule, "int", parentUID, noneFound=False)
		if isInt:
			value = int(value)
		return min(max(value, minval), maxval)

class anyType(DataType):
	def __init__(self, jbk):
		super().__init__(jbk)
		self.name = "any"
		self.default = None
	#returns true/false, whether or not the data is this type
	def matches(self, data):
		return True
	def convert(self, data, rule, parentUID="ROOT"):
		return data

class boolean(DataType):
	def __init__(self, jbk):
		super().__init__(jbk)
		self.name = "bool"
		self.t = bool
		self.default = False

	def convert(self, data, rule, parentUID="ROOT"):
		return data == True


class arrayType(DataType):
	def __init__(self, jbk):
		super().__init__(jbk)
		self.name = "array"
		self.t = list
		self.default = []

	def convert(self, data, rules, parentUID="ROOT"):
		#length
		minLength = self.jbk.get_property(rules, "minLength", parentUID, noneFound=0)
		maxLength = self.jbk.get_property(rules, "maxLength", parentUID, noneFound=math.inf)
		if len(data) < minLength:
			self.jbk.error(f"Array too short!")
		if len(data) > maxLength:
			data = data[:maxLength]
		if 'rule' not in rules:
			defType = self.jbk.get_property(rules, "rule", parentUID, noneFound=self.jbk.get_object(parentUID)['_defaults']['t'])
			if defType == "array": defType = "string"
			rules['rule'] = {"t": defType}
		
		for x,i in zip(data, range(0, len(data))):
			#convert single
			usedRule = rules['rule']
			#check if we have any custom defined rules
			if f"rule#{i}" in rules:
				usedRule = rules[f'rule#{i}']
			data[i] = self.jbk.convert_single(x, usedRule, parentUID=parentUID, name=x)
		return data
