from copy import deepcopy, copy
from ..jsonbyket import jsonbyket
from .basics import DataType

class dictList(DataType):
	def __init__(self, jbk: jsonbyket):
		super().__init__(jbk)
		self.name = "keyvaluepair"
		self.t = dict
		self.jbk = jbk
		self.default = {}
	def matches(self, data):
		return super().matches(data)
	def convert(self, data, ruleset, parentUID="ROOT"):
		if 'rule' not in ruleset:
			ruleset['rule'] = {}
		#now we basically go through each item in the data, convert it using the ruleset['rule'] as the ruleset and the item as the data
		for key in data:
			data[key] = self.jbk.convert_single(
					data[key],
					ruleset['rule'],
					parentUID=parentUID,
					name=key)
		return data



class dictType:
	def __init__(self, ajson : jsonbyket):
		self.name = "object"
		self.jbk = ajson
		self.t = dict
		self.default = {}
	#returns true/false, whether or not the data is this type
	def matches(self, data):
		if type(data) == dict:
			return True
		return False
	def convert(self, data, ruleset, parentUID="ROOT"):#this ones different, since it's a dictionary, therefore it has multiple values of different types (including other dictionaries/objects)
		parent = self.jbk.get_object(parentUID)
		data['_defaults'] = {} #reserved property defaults
		data['_variables'] = {} #reserved property variables
		#set defaults to parent's defaults, then override some of them. 
		data['_defaults'] = deepcopy(parent['_defaults'])
		_ruleset = ruleset
		rules = self.jbk.get_property(ruleset, 'rules', parentUID) #propertyName, propertyRules
		ruleset = None
		for propertyName, ruleset in rules.items(): #iterating through "propertyName": {"t": "string", "d": "no"} type of stuff
			if propertyName.startswith("//"): #ignore, this is a comment
				continue

			#region rule file only	
			if propertyName.startswith("@@"): 
				#this sets the settings of jsonbyket. 
				# In this case, the ruleset is not actually a ruleset, but the new value for the setting
				# Generally, this is for things like logging levels and whatnot.
				self.jbk.set_value(self.jbk.globals, propertyName.split("@@")[1], ruleset)
				continue
			
			if propertyName[0] == "@":
				#this overrides default settings
				#in this case, the ruleset is the new value of whatever is being overriden.
				#get the parent that this refers to. as in, are there any periods after @?
				target_parent = data["_uid"]
				targetRule = propertyName.split("@")[1]
				if propertyName[1] == ".": #go up a level or two. or more.
					target_parent = self.jbk.get_parent(target_parent, level=propertyName.count("."))["_uid"]
					targetRule = propertyName.split("@" + (propertyName.count(".") * ".") )[1] #this works, don't question it.
				self.jbk.set_value(self.jbk.get_object(target_parent)['_defaults'],
					targetRule,
					ruleset)
				continue

			#endregion
			if propertyName not in data: #a property was not found in the config, and this property is required.
				if self.jbk.get_property(ruleset, "r", parentUID, noneFound=data["_defaults"]['r']):
					raise Exception(f"Property with key \"{propertyName}\" was not found in the config file. ")
			
			autoAdd = self.jbk.get_property(ruleset, "autoAdd", parentUID, noneFound=data["_defaults"]['autoAdd'])
			#if this property wasn't supplied, and autoAdd is enabled
			if propertyName not in data and autoAdd:
				#add the property, assign it to it's default value
				data[propertyName] = self.jbk.get_default(ruleset, data)
			if propertyName not in data and autoAdd == False:
				continue
			
			#check if this makes a variable. if so, set the variable to the value.
			if "varSet" in ruleset:
				self.jbk.log(f"Setting variable {ruleset['varSet']}", level=-1)
				varToSet = ruleset['varSet']
				target_parent_level = 0
				for x in copy(varToSet):
					if x == ".":
						target_parent_level += 1
						varToSet = varToSet[1:]
					else:
						break
				targetObject = self.jbk.get_parent(data, level=target_parent_level)
				targetObject['_variables'][varToSet] = data[propertyName]
			
			if propertyName in data:
				data[propertyName] = self.jbk.convert_single(
					self.jbk.get_property(data, propertyName, parentUID),
					ruleset,
					parentUID=data["_uid"],
					name=propertyName)
		return data