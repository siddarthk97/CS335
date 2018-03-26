import sys 
from parser import parser
import collections

class IR:

	def __init__(self,filename):
		irfile = open(filename, 'r')
		ircode = irfile.read()
		ircode = ircode.strip('\n')

		# Consruct the instruction list
		self.instrlist = []
		self.instrlist = ircode.split('\n')
		self.operators = ['=', '+', '-', '<<', '>>', '/', '*', 'scan']

		self.instrtype = ['=', '+', '-', '<<','>>','<','>' ,'/', '*', '%', '&&', 'conditional_goto', 'goto', 'fn_call', 'fn_def', 'print', 'scan', 'return', 'exit',]
		self.Blocks = self.Build_Blocks() #  dict { leader_no. : last_line_no }
		self.address_descriptor = {}
		self.variable_list = self.Build_varlist()
		# list of dicts(blocks) where each key(variables) is a list pf list (use lines of that var in that live range)
		self.next_use_table, self.lineVars = self.Build_next_use_table() 

	def Build_Blocks(self):
		Blocks = {}
		# get leaders
		leaders = [1]
		for instr in self.instrlist:
			instr = instr.split(', ')
			if((instr[1]=='conditional_goto') or (instr[1] == 'goto')):
				leaders.append(int(instr[0])+1)
			if(instr[1] == 'label'):
				leaders.append(int(instr[0]))
			if((instr[1]=='fn_call_1') or (instr[1]=='fn_call_2') or (instr[1]=='fn_def')):
				leaders.append(int(instr[0]))

		leaders = list(set(leaders))
		leaders.sort()
		for i in range(len(leaders)-1):
			Blocks[leaders[i]] = leaders[i+1]-1

		Blocks[leaders[-1]] = int(self.instrlist[-1].split(', ')[0])

		Blocks = collections.OrderedDict(sorted(Blocks.items()))
		return Blocks


	def Build_varlist(self):
		varz = []
		for instr in self.instrlist:
			instr = instr.split(', ')
			if(instr[1] in self.operators):
				var = instr[2]
				if(var not in varz):
					varz.append(var)

			elif instr[1] == 'fn_call_2':
				varz.append(instr[-1])
		for x in varz:
			self.address_descriptor[x] = x
		return varz

	def Build_next_use_table(self):
		table = {} # dict of dicts of dicts
		lineVars = {}
		for start, end in self.Blocks.items():	
			line = {}
			line_2 = {}
			for i in range(end, start-1, -1):
				if start == end:
					line[i] = {}

				else:
					if i is not end:
						instr = self.instrlist[i]
						instr = instr.split(', ')
						line[i] = dict(line[i+1])
						for v in varz["killed"]:
							line[i][v] = 0
						for v in varz["used"]:
							line[i][v] = int(instr[0])
					else:
						line[i] = {}
				instr = self.instrlist[i-1]
				instr = instr.split(', ')
				varz = parser(instr, self.variable_list)

				line_2[i] = []
				for v in varz["killed"]:
					line_2[i].append(v)
				for v in varz["used"]:
					line_2[i].append(v)

			table[start] = line
			lineVars[start] = line_2
		return table,lineVars