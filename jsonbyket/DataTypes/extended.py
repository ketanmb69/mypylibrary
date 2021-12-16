from jsonbyket.DataTypes.basics import DataType
from ..utils import seperate_string_number
import math
from ..jsonbyket import jsonbyket

class choice(DataType):
	def __init__(self, jbk):
		super().__init__(jbk)
		self.name = "choice"
		self.t = any

	def matches(self, data):

		return type(data) not in [dict, list]
	
	def convert(self, data, ruleset, parentUID="ROOT"):
		options = self.jbk.get_property(ruleset, "options",
			parentUID=parentUID,
			noneFound=self.jbk.get_parent(parentUID)['_defaults']['options'])
		if data not in options:
			self.jbk.error(f"\"{data}\" is not a valid option. It should be one of the following: {', '.join(options)}")
		else:
			return data
		

	