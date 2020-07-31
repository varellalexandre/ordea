from ortools.linear_solver import pywraplp
from typing import Optional
import pandas as pd
import json
import copy
class PDEA:
	def __get_inputs(self)->list:
		inputs = []
		for bundle_element in self.bundles:
			for input_element in bundle_element['I']:
				if input_element not in inputs:
					inputs.append(input_element)
		return copy.deepcopy(inputs)

	def get_objective(self,dmu:pd.Series)->pywraplp.Solver.Objective:
		objective_function = self.solver.Objective()
		for output_element in self.__get_outputs():
			objective_function.SetCoefficient(self.solver.\
												LookupVariable('u{}'.format(output_element)),
												float(dmu[output_element])
											)
		return objective_function


	def __get_outputs(self)->list:
		outputs = []
		for bundle_element in self.bundles:
			for output_element in bundle_element['R']:
				if output_element not in outputs:
					outputs.append(output_element)
		return copy.deepcopy(outputs)

	def __get_paths(self)->list:
		lista = list()
		for bundle_element in self.bundles:
			for bundle_output in bundle_element['R']:
				aux = dict()
				aux['R'] = [bundle_output]
				aux['I'] = list(bundle_element['I'])
				lista.append(dict(aux))
		return copy.deepcopy(lista)

	def __get_sub_var(self,input_element:str)->list:
		lista = []
		for index,bundle_element in enumerate(self.bundles):
			if input_element in bundle_element['I']:
				lista.append('w{}{}'.format(input_element,index))
		return copy.deepcopy(lista)

	def get_variables(self,eps:float)->list:
		inputs = self.__get_inputs()
		outputs = self.__get_outputs()
		variables = []
		for input_element in inputs:
			self.solver.NumVar(eps,self.solver.infinity(),'v{}'.format(input_element))
			variables.append('v{}'.format(input_element))
			for sub_variable in self.__get_sub_var(input_element):
				self.solver.NumVar(eps,self.solver.infinity(),sub_variable)
				variables.append(sub_variable)
		for output_element in outputs:
			self.solver.NumVar(eps,self.solver.infinity(),'u{}'.format(output_element))
			variables.append('u{}'.format(output_element))
		return copy.deepcopy(variables)

	def __get_restriction_b(self,dmu:pd.Series)->list:
		#Referido no artigo Imanirad et. al.(2015)
		#SUM vi*Xij0 = 1
		restriction_list = list()
		restriction_list.append(self.solver.Constraint(1,1))
		for input_element in self.__get_inputs():
			input_var = self.solver.LookupVariable('v{}'.format(input_element))
			restriction_list[-1].SetCoefficient(input_var,float(dmu[input_element]))
		return restriction_list

	def __get_restriction_c(self)->list:
		#Referido no artigo Imanirad et. al.(2015)
		#SUM urYrj - SUM (gama)ikpXij <=0
		restriction_list = list()
		for _,dmu in self.set.iterrows():
			for bundle_element in self.bundles:
				restriction_list.append(self.solver.Constraint(-self.solver.infinity(),0))
				for output_element in bundle_element['R']:
					restriction_list[-1].SetCoefficient(self.solver.\
											LookupVariable('u{}'.format(output_element)),
											float(dmu[output_element])
										)
				for index,input_element in enumerate(bundle_element['I']):
					restriction_list[-1].SetCoefficient(self.solver.\
													LookupVariable('w{}{}'.format(input_element,index)),
													float(-dmu[input_element])
												)
		return restriction_list

	def __get_restriction_d(self)->list:
		#Referido no artigo Imanirad et. al.(2015)
		#(gama)ikp=Vi
		restriction_list = list()
		for input_element in self.__get_inputs():
			variable = self.solver.LookupVariable('v{}'.format(input_element))
			restriction_list.append(self.solver.Constraint(0,0))
			restriction_list[-1].SetCoefficient(variable,-1)
			for sub_variable in self.__get_sub_var(input_element):
				restriction_list[-1].SetCoefficient(self.solver.\
										LookupVariable(sub_variable),
										1)
		return restriction_list

	def __get_restriction_e(self)->list:
		#Referido no artigo Imanirad et. al.(2015)
		#Restringe os limites
		#vaikp<=(gama)ikp<=Vibikp
		restriction_list = list()
		input_elements = self.__get_inputs()
		for node_element in self.diagram:
			if node_element['name'] in input_elements:
				for sub_variable in self.__get_sub_var(node_element['name']):
					#Menor ou igual
					restriction_list.append(self.solver.Constraint(-self.solver.infinity(),0))
					variable_x = self.solver.LookupVariable("v{}".format(node_element['name']))
					sub_variable_x = self.solver.LookupVariable("{}".format(sub_variable))
					restriction_list[-1].SetCoefficient(variable_x,float(node_element['range'][0]))
					restriction_list[-1].SetCoefficient(sub_variable_x,-1)
					#Maior ou igual
					restriction_list.append(self.solver.Constraint(0,self.solver.infinity()))
					variable_x = self.solver.LookupVariable("v{}".format(node_element['name']))
					sub_variable_x = self.solver.LookupVariable("{}".format(sub_variable))
					restriction_list[-1].SetCoefficient(variable_x,float(node_element['range'][1]))
					restriction_list[-1].SetCoefficient(sub_variable_x,-1)
		return restriction_list

	def __get_bundles(self,file:str)->list:
		def compare_dependencies(variable_inputs:list,bundle_inputs:list)->bool:
			if len(variable_inputs) != len(bundle_inputs):
				#	Caso a quantidade de inputs seja diferente
				#a variável não pertence ao bundle retornando falso
				return False
			else:
				for input_element in variable_inputs:
					#	Verifica se todos os elementos de input da variável
					#estão contídos nos inputs do bundle
					if input_element in bundle_inputs:
						continue
					else:
						return False
			return True


		with open(file) as file_schema:
			data = json.load(file_schema)
			file_schema.close()
		self.diagram = data
		bundles = []
		for variable in self.diagram:
			if len(variable["depends"]) < 1:
				continue
			for bundle_element in bundles:
				#Tenta encaixar uma variável em um bundle
				if compare_dependencies(variable["depends"],bundle_element['I']):
					bundle_element['R'].append(variable["name"])
					break
			else:
				aux = dict()
				aux["I"] = list(variable["depends"])
				aux["R"] = [variable["name"]]
				bundles.append(aux)
		return copy.deepcopy(bundles)

	def get_restrictions(self,dmu)->list:
		restrictions = 	self.__get_restriction_b(dmu)+\
						self.__get_restriction_c()+\
						self.__get_restriction_d()+\
						self.__get_restriction_e()
		return list(restrictions)

	def __get_coef(self,element)->list:
		aux = dict()
		for variable in self.solver.variables():
			aux[variable.name()] = element.GetCoefficient(variable)
		aux['lb'] = element.lb()
		aux['ub'] = element.ub()
		return copy.deepcopy(aux)

	def solve(self)->list:
		results = list()
		for i,dmu in self.set.iterrows():
			self.solver = pywraplp.Solver('PartialDEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.variables = self.get_variables(self.eps)
			self.obj = self.get_objective(dmu)
			self.restrictions = self.get_restrictions(dmu)
			result = self.solver.Solve()
			aux = dict()
			for variable in self.variables:
				aux[variable] = self.solver.LookupVariable(variable).solution_value()
			aux['Resultado'] = result
			results.append(aux)
		return copy.deepcopy(results)


	def __init__(self,
				file:str,
				dataset:pd.DataFrame,
				eps:Optional[float] = 0.000000999999):

		self.set = pd.DataFrame(dataset)
		self.file = file
		self.bundles = self.__get_bundles(file)
		self.paths = self.__get_paths()
		self.eps = eps