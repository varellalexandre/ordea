from ortools.linear_solver import pywraplp
import pandas as pd
import json
class PDEA:
	def get_inputs(self):
		inputs = []
		for i in self.bundles:
			for j in i['I']:
				if j not in inputs:
					inputs.append(j)
		return list(inputs)

	def get_objective(self,dmu):
		for i,out in enumerate(self.get_outputs()):
			self.obj.SetCoefficient(self.solver.\
				LookupVariable('u{}'.format(out)),
				float(dmu[out])
			)
		self.obj.SetMaximization()


	def get_outputs(self):
		outputs = []
		for i in self.bundles:
			for j in i['R']:
				if j not in outputs:
					outputs.append(j)
		return list(outputs)

	def get_paths(self):
		lista = []
		try:
			type(self.bundles)
		except:
			self.bundles = self.get_bundles(self.file)
		for index, i in enumerate(self.bundles):
			for j in i['R']:
				aux = dict()
				aux['R'] = [j]
				aux['I'] = list(i['I'])
				lista.append(dict(aux))
		return lista

	def get_sub_var(self,k):
		lista = []
		for index,i in enumerate(self.bundles):
			if k in i['I']:
				lista.append('w{}{}'.format(k,index))
		return list(lista)

	def get_variables(self,eps):
		inp = self.get_inputs()
		out = self.get_outputs()
		variables = []
		for i in inp:
			self.solver.NumVar(eps,self.solver.infinity(),'v{}'.format(i))
			variables.append('v{}'.format(i))
			for k in self.get_sub_var(i):
				self.solver.NumVar(eps,self.solver.infinity(),k)
				variables.append(k)
		for i in out:
			self.solver.NumVar(eps,self.solver.infinity(),'u{}'.format(i))
			variables.append('u{}'.format(i))
		return list(variables)

	def restriction_b(self,dmu):
		self.restrictions.append(self.solver.Constraint(1,1))
		for i in self.get_inputs():
			inp_var = self.solver.LookupVariable('v{}'.format(i))
			actual = len(self.restrictions)-1
			self.restrictions[actual].SetCoefficient(inp_var,float(dmu[i]))
		return 

	def restriction_c(self):
		for ind,dmu in self.set.iterrows():
			for index,i in enumerate(self.bundles):
				self.restrictions.append(self.solver.Constraint(-self.solver.infinity(),0))
				actual = len(self.restrictions)-1
				for out in i['R']:
					self.restrictions[actual].\
						SetCoefficient(self.solver.\
							LookupVariable('u{}'.format(out)),
							float(dmu[out])
						)
				for inp in i['I']:
					self.restrictions[actual].\
						SetCoefficient(self.solver.\
							LookupVariable('w{}{}'.format(inp,index)),
							float(-dmu[inp])
						)
		return

	def restriction_d(self):
		for k in self.get_inputs():
			var = self.solver.LookupVariable('v{}'.format(k))
			self.restrictions.append(self.solver.Constraint(0,0))
			actual = len(self.restrictions)-1
			self.restrictions[actual].SetCoefficient(var,-1)
			lista = self.get_sub_var(k)
			for i in lista:
				sub_var = self.solver.LookupVariable(i)
				self.restrictions[actual].SetCoefficient(sub_var,1)

	def restriction_e(self):
		inp = self.get_inputs()
		for i in self.organization:
			if i['name'] in inp:
				lista = self.get_sub_var(i['name'])
				for k in lista:
					#Menor ou igual
					self.restrictions.append(self.solver.Constraint(-self.solver.infinity(),0))
					actual = len(self.restrictions)-1
					var_x = self.solver.LookupVariable("v{}".format(i['name']))
					sub_var_x = self.solver.LookupVariable("{}".format(k))
					self.restrictions[actual].SetCoefficient(var_x,float(i['range'][0]))
					self.restrictions[actual].SetCoefficient(sub_var_x,-1)
					#Maior ou igual
					self.restrictions.append(self.solver.Constraint(0,self.solver.infinity()))
					actual = len(self.restrictions)-1
					var_x = self.solver.LookupVariable("v{}".format(i['name']))
					sub_var_x = self.solver.LookupVariable("{}".format(k))
					self.restrictions[actual].SetCoefficient(var_x,float(i['range'][1]))
					self.restrictions[actual].SetCoefficient(sub_var_x,-1)


	def get_bundles(self,file):
		def compare_dependencies(a,b):
			if len(a) != len(b):
				return False
			else:
				for el in a:
					if el in b:
						continue
					else:
						return False
			return True
		with open(file) as infile:
			data = json.load(infile)
		self.organization = data
		bundles = []
		for index,i in enumerate(self.organization):
			if len(i["depends"]) < 1:
				continue
			for j in bundles:
				if compare_dependencies(i["depends"],j['I']):
					j['R'].append(i["name"])
					break
			else:
				aux = dict()
				aux["I"] = list(i["depends"])
				aux["R"] = [i["name"]]
				bundles.append(aux)
		return list(bundles)

	def get_restrictions(self,dmu):
		self.restriction_b(dmu)
		self.restriction_c()
		self.restriction_d()
		self.restriction_e()
		
	def get_coef(self,element):
		aux = dict()
		for j in self.solver.variables():
			aux[j.name()] = element.GetCoefficient(j)
		aux['lb'] = element.lb()
		aux['ub'] = element.ub()
		return aux

	def __init__(self,file,dataset,path = 'resp_partial.xlsx' ,eps = 0.000000999999,save_dmu = False):
		self.set = dataset
		resposta = []
		self.file = file
		writer = pd.ExcelWriter(path, engine='xlsxwriter')
		for i,dmu in self.set.iterrows():
			coef = []
			self.solver = pywraplp.Solver('PartialDEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.obj = self.solver.Objective()
			self.bundles = self.get_bundles(file)
			self.paths = self.get_paths()
			self.variables = self.get_variables(eps)
			self.restrictions = []
			self.get_objective(dmu)
			self.get_restrictions(dmu)
			for j in self.restrictions:
				coef.append(self.get_coef(j))
			resultado = self.solver.Solve()
			if save_dmu == True:
				pd.DataFrame(coef).to_excel(writer,sheet_name='DMU-{}'.format(i))
			aux = dict()
			for j in self.variables:
				aux[j] = self.solver.LookupVariable(j).solution_value()
			aux['Resultado'] = resultado
			resposta.append(aux)
		res = pd.DataFrame(resposta)
		for i in self.get_inputs():
			for index, var in enumerate(self.get_sub_var(i)):
				nome = i+"{}".format(index+1)
				res[nome] = res[var]/res["v"+i]
		self.frame = res

	