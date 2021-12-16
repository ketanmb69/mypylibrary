import json, os, sys, traceback, copy, argparse
from math import exp
import colorama

from colorama.ansi import Fore

class DBG:
	def __init__(self, devmode):
		self.colors = {"red": Fore.RED, "green": Fore.GREEN, "blue": Fore.BLUE, "yellow": Fore.YELLOW, "orange": Fore.LIGHTRED_EX, "purple": Fore.MAGENTA}
		colorama.init() #for testing
	def print(self, *args, color="green"):
		c = Fore.CYAN
		if color in self.colors: c = self.colors[color]
		print(c + "", *args)
		print(colorama.Style.RESET_ALL)


class jsonbyket:
	def __init__(self):
		from .utils import seperate_string_number
		from .DataTypes import DefaultTypes
		from .VarTypes import DefaultVarTypes
		self.debugger = DBG(True)
		self.print = self.debugger.print

		self.init_self_variables()
		self.dataTypes = {}
		self.varTypes  = {}
		self.transforms = {}
		DefaultTypes.LoadDefaultDatatypes(self) 
		DefaultVarTypes.LoadDefaultVarTypes(self)
	
	def init_self_variables(self):
		"""Initializes variables/resets most data
		"""
		self.vars      = {}
		self.data      = {} 
		self.objects   = {"ROOT": self.data}
		self.uidLevel = 0 
		self.globals = {"logging": 4, "tracebackLogging": False, "removeHidden": True}
		self.defaults = {
			"unit": {"time": "s", "distance": "m"},
			"autoAdd": True,
			"t": "string",
			"r" : False,
			"options": ["yes", "no"]
		}
		self.data["_defaults"] = self.defaults
		self.data["_uid"] = "ROOT"
		self.data["_variables"] = self.vars
		self.data['_parent'] = "ROOT"

	def add_data_type(self, dataType):
		"""Adds a new DataType to this jsonbyket object.

		Args:
			dataType (DataType): The DataType to add.
		"""
		dataTypeInstance = dataType(self)
		self.dataTypes[dataTypeInstance.name] = dataTypeInstance
	
	def add_var_type(self, varType):
		"""Adds a variable type to this jsonbyket object

		Args:
			varType (VarType): The variable type to add
		"""
		varTypeInstance = varType(self)
		self.varTypes[varTypeInstance.name] = varTypeInstance
	
	def add_transform(self, transform, name=""):
		"""Adds a transform to this jsonbyket object

		Args:
			transform (function): The function used to transform the property (after processing)
			name (str, optional): The name of the transformation. Defaults to "".
		"""
		if name == "": name = transform.__name__
		self.transforms[name] = transform

	def load(self, jsonFile, ruleFile):
		"""Loads from a file

		Args:
			jsonFile (path): The file to load data from
			ruleFile (path): The file containing the rules.
		"""
		data = None
		self.rules = None
		try:
			with open(jsonFile, "r") as f:
				dataString = f.read()
		except:
			self.error(f"Could not find file \"{jsonFile}\"")
		try:
			with open(ruleFile, "r") as f:
				rulesString = f.read()
		except:
			self.error(f"Could not find rules file \"{ruleFile}\"")
		
		self.loads(dataString, rulesString)
	
	def loads(self, data, rules):
		"""Loads data from a string

		Args:
			data (string): The json data
			rules (string): The rules for the json data
		"""
		data = json.loads(data)
		self.rules = json.loads(rules)
		return self.load_dict(data, self.rules)
		
	def load_dict(self, data, rules):
		"""Loads data from a dictionary

		Args:
			data (dict): The data provided by the user
			rules (dict): The rules provided by the developer
		"""
		self.rules = rules
		return self.convert_all(data, rules)

	def remove_keys(self, d, keys=["_parent", "_uid", "_variables", "_defaults"]):
		doItAgain = False
		for key in d:
			if key in keys:
				#reMOVE
				del d[key]
				doItAgain = True
				break
			if type(d[key]) == dict: #recursive
				self.remove_keys(d[key], keys=keys)
			if type(d[key]) == list:
				for item in d[key]:
					if type(item) == dict:
						self.remove_keys(item, keys=keys)
		if doItAgain:
			self.remove_keys(d, keys=keys)

	def convert_all(self, data, rules): 
		self.init_self_variables()
		self.data = self.convert_single(data, {"t": "object", "rules": rules}, parentUID="ROOT", name="root", setUID="ROOT")
		if self.globals['removeHidden']:
			self.remove_keys(self.data)
		return self.data
	
	def convert_single(self, property, ruleset, setUID=None, parentUID="ROOT", name=""):
		if type(property) == str:
			try:
				property = property.split("//")[0]
			except:
				pass
		#Generate UID
		uid = setUID
		if uid == None:
			uid = self.generate_uid()
		if 'transforms' not in ruleset: ruleset['transforms'] = []
		expectedType = self.get_property(ruleset, "t", parentUID, noneFound="any").split(":")[0]
		if expectedType in self.dataTypes:
			property = self.test_variable(property, parentUID, ruleset)
			isValid = self.dataTypes[expectedType].matches(property)
			if isValid:

				if type(property) == dict and expectedType != "keyvaluepair":
					property["_uid"] = uid
					property["_parent"] = parentUID
					if uid not in self.objects:
						self.objects[uid] = property
					else:
						self.merge_dicts(self.objects, property)
					property = self.dataTypes[expectedType].convert(property, ruleset, parentUID=parentUID)
					property = self.apply_transforms(property, ruleset, parentUID)
				elif type(property) == list:
					property = self.dataTypes[expectedType].convert(property, ruleset, parentUID=parentUID)
					property = self.apply_transforms(property, ruleset, parentUID)
				else:
					property = self.dataTypes[expectedType].convert(property, ruleset, parentUID=parentUID)
					property = self.apply_transforms(property, ruleset, parentUID)
			else:
				self.error(f"Property \"{name}\" is supposed to be {expectedType}. Got \"{type(property).__name__}\" instead.")
		else:
			raise Exception(f"Invallid DataType \"{expectedType}\"")
		return property
	

	def apply_transforms(self, property, ruleset, parentUID):
		t = self.get_property(ruleset, "t", parentUID, noneFound="any")
		if ":" in t:
			for transform in t.split(":")[1].split(","):
				ruleset['transforms'].append(transform)
			ruleset['t'] = t.split(":")[0]
		for transform in ruleset['transforms']:
			if transform == "": continue
			if transform not in self.transforms:
				raise Exception(f"Transform \"{transform}\" does not exist or was never added.")
			property = self.transforms[transform](property, ruleset, self, parentUID)
		return property

	def get_parent(self, propertyUID, level=1):
		"""Gets the parent of an object

		Args:
			propertyUID (string, dictionary): Either the UID of the property, or the property itself.
			level (int, optional): How many levels to go up. Defaults to 1.

		Returns:
			[string]: UID of the parent. 
		"""
		"""
		Parent structure from the perspective of "ParentC"
		ROOT - level = 3 (all the way to infinity!)
		ROOT - level = 2
			ParentB - level = 1
				ParentC - level = 0
		"""
		#get the UID of the data object.
		uid = propertyUID
		if type(propertyUID) == dict: uid = propertyUID['_uid']
		
		parent = self.get_object(uid)['_uid'] 
		for x in range(0, level): 
			parent = self.get_object(parent)["_parent"]
		
		return self.get_object(parent)
	
	def get_object(self, UID):
		"""Gets an object from a specified UID

		Args:
			UID (string): The UID of the target object.
		Raises:
			Exception - The object wasn't found
		Returns:
			[dictionary]: The object we're looking for.
		"""
		if UID not in self.objects:
			raise Exception("Object not found")
		return self.objects[UID]

	def generate_uid(self):
		"""Generates a unique identifier as a string.

		Returns:
			[string]: The newly generated UID
		"""
		self.uidLevel += 1
		return str(self.uidLevel)
	
	def get_default(self, ruleset, property):
		#enforce types
		if "t" not in ruleset:
			ruleset['t'] = self.get_property(property['_defaults'], 't', property['_parent']) #default is "string"

		if "d" in ruleset:
			defaults = self.get_property(ruleset, "d", property["_parent"])
			if type(defaults) == list and ruleset['t'] != "array":

				for d in defaults:
					newD = self.get_property({'a':d}, 'a', property['_uid'])
					if self.dataTypes[ruleset['t']].matches(newD):
						return newD
				return None
			else:
				return defaults

		return copy.deepcopy(self.dataTypes[ruleset['t']].default) 
	
	def test_variable(self, property, parentUID, ruleset, root=0, checked=""):
		checked += "/" + parentUID
		if type(property) == str and property.startswith("$"):
			if property.startswith("$$"):
				parentLevel = property.count(".")
				variable = property.split("$$" + (property.count(".") * ".") )[1]

				target_parent = self.get_parent(parentUID, level = parentLevel)
				if variable in target_parent["_variables"]:
					return target_parent["_variables"][variable]
				else:
				
					if parentUID == "ROOT":
						root += 1
					if root < 2:
						next = target_parent['_uid']
						if next == parentUID:
							next = target_parent["_parent"]

						return self.test_variable(property, next, ruleset, root=root, checked=checked)
					self.warn(f"Variable \"{variable}\" does not exist!", checked)
			else:
				varTypeName = property.split("$")[1].split(" ")[0]
				if varTypeName in self.varTypes:
					varType = self.varTypes[varTypeName]
					if varType == None:
						raise Exception(f"No such varType \"{varTypeName}\"")
					else:
						return varType.get_value(ruleset, property)
		return property
	
	def get_property(self, dictionary: dict, key: str, parentUID: str, noneFound=None):
		"""Gets a value from a dictionary with a given key. Also tests for variables.

		Args:
			dictionary (dict): The dictionary to retrieve from
			key (str): The key to use
			parentUID (str): The UID of the parent. This is used to test variables
			noneFound (any, optional): The value to return if nothing is found. Defaults to None.

		Returns:
			[any]: The property you're looking for.
		"""
		if key not in dictionary:
			return noneFound
		else:
			return self.test_variable(dictionary[key], 
			parentUID, 
			dictionary)
	
	def merge_dicts(self, d1, d2):
		"""Puts D2 into D1.

		Args:
			d1 ([type]): [description]
			d2 ([type]): [description]

		Returns:
			[type]: [description]
		"""
		for x in d2:
			if type(d2[x]) not in [dict, list] or x not in d1:
				d1[x] = d2[x]
			elif type(d2[x]) == dict:
				self.merge_dicts(d1[x], d2[x])
			elif type(d2[x]) == list:
				d1[x] = copy.deepcopy(d2[x])
		return True
			
	def set_value(self, dictionary:dict, key:str, newValue):
		"""Sets the value of a dictionary without overwriting everything if the new value is a dictionary.
		Args:
			dictionary (dict): [description]
			key (str): [description]
			newValue (any): [description]
		"""
		self.merge_dicts(dictionary, {key: newValue})
	
	def error(self, *args):
		print(colorama.Fore.RED+"", *args)
		if self.globals['tracebackLogging']:
			raise Exception(*args)
		sys.exit()
	
	def warn(self, *args, level=4):
		if self.globals['logging'] <= level:
			print(colorama.Fore.YELLOW, *args)

	def log(self, *args, **kw):
		level = kw.get('level', 0)
		error = kw.get('error', False)
		warning = kw.get('warning', False)
		if error:
			level = 5
		if warning:
			level = 4
		if self.globals['logging'] > level:
			return
		out = kw.get('file',sys.stdout)
		linesep= kw.get('end','\n')
		colsep= kw.get('sep',' ')

		tb = traceback.format_stack()
		tbtxt = "\n" + tb[len(tb)-2].split("\n")[0] + "\n"
		if self.globals['tracebackLogging'] == False:
			tbtxt = ""
		if error:
			raise Exception(colsep.join(map(str,args)))
		
		out.write(tbtxt + colsep.join(map(str,args)))
		out.write(linesep)

