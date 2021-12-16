from .basics import number, seperate_string_number, DataType

class unit(DataType):
	def __init__(self, jbk, name, default, units={}):
		super().__init__(jbk)
		self.name = name
		self.t = str
		self.default = default
		self.units = units
	
	def matches(self, data):
		if type(data) == str:
			if seperate_string_number(data)[1] in self.units:
				return True
			else:
				self.jbk.log(f"Error: {self.name} does not recognize \"{seperate_string_number(data)[1]}\" as a valid unit.", level=5)
		return False
	def convert(self, data, rule, skipRuleConversion=False, useUnit=None, parentUID="ROOT"):
		unitToUse = self.jbk.get_object(parentUID)['_defaults']['unit'][self.name]
		if skipRuleConversion == False:
			if "unit" in rule:
				unitToUse = rule['unit']
		if useUnit != None:
			unitToUse = useUnit
		
		if skipRuleConversion == False:
			alsoConvert = ["min", "max", "multiplier"]
			for x in alsoConvert:
				if x in rule:
					rule[x] = self.convert(rule[x], rule, skipRuleConversion=True, useUnit=unitToUse)
		
		value = seperate_string_number(data) 
		valueInDefaultUnits = self.units[value[1]] * float(value[0]) 

		valueInDesiredUnits = valueInDefaultUnits / self.units[unitToUse] 
		numberValue = self.jbk.dataTypes['number'].convert(valueInDesiredUnits, rule, parentUID=parentUID)
		return numberValue


class time(unit):
	def __init__(self, ajson):
		super().__init__(ajson, "time", "0s", units={"ms":1/1000, "μs": 1/1000000, "us": 1/1000000, "ns": 1/(1000000000), "":1, "sec": 1, "secs": 1, "s": 1, "m": 60, "min": 60, "mins": 60, "h": 60*60, "d": 60*60*24, "W": 60*60*24*7, "M": 60*60*24*7*30, "Y": 60*60*24*365})

class distance(unit):
	def __init__(self, ajson):
		super().__init__(ajson, "distance", "0m", units={"":1, "me": 1, "m": 1, "km": 1000, "ft": 3.280839895, "mi": 1000 * 0.621371, "cm": .001, "in": 3.280839895/12})
