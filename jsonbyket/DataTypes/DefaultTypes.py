from .basics import anyType, arrayType, string, number, boolean
from .dictType import dictType, dictList
from .units import distance, time
from .extended import choice
def LoadDefaultDatatypes(jbkObject):
	dts = [anyType, arrayType, dictType, distance, string, number, boolean, time, choice, dictList]
	for x in dts:
		jbkObject.add_data_type(x)
