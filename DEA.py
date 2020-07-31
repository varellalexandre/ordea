from ortools.linear_solver import pywraplp
import pandas as pd
import copy
#Objeto DEA para cálculo do algoritmo DEA
#Ao iniciar o objeto basta passar os inputs e 
#outputs desejados. O retorno das funções de 
#cálculo é um dataframe
class DEA:
	def __init__(self,input:list,output:list):
		if len(input) == len(output):
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			self.entries = input
			self.out = output
			self.incoef = []
			self.outcoef = []
			self.constraints = []
		else:
			raise Exception("Number of DMUs in inputs are different from the output")
	
	def __bcc_input_primal(self)->list:
		resposta = []
		for dmu in range(len(self.entries)):
			#Definindo as variáveis
			self.incoef = []
			self.outcoef = []
			self.constraints = []
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			for i in range(len(self.entries[0])):
				self.incoef.append(self.solver.NumVar(0,self.solver.infinity(),'v'+str(i)))
			for i in range(len(self.out[0])):
				self.outcoef.append(self.solver.NumVar(0,self.solver.infinity(),'u'+str(i)))
			self.bias = self.solver.NumVar(-self.solver.infinity(),self.solver.infinity(),'b')
			#Definindo a função objetivo
			for i in range(len(self.outcoef)):
				self.objective.SetCoefficient(self.outcoef[i],self.out[dmu][i])
			self.objective.SetCoefficient(self.bias,1)
			self.objective.SetMaximization()
			#Definindo as restrições
			#Restrição de que todos os valores devem ter inputs maiores que outputs
			for i in range(len(self.entries)):
				self.constraints.append(self.solver.Constraint(-self.solver.infinity(),0))
				self.constraints[i].SetCoefficient(self.bias,1)
				for j in range(len(self.incoef)):
					self.constraints[i].SetCoefficient(self.incoef[j],-1*self.entries[i][j])
				for k in range(len(self.outcoef)):
					self.constraints[i].SetCoefficient(self.outcoef[k],self.out[i][k])
			#Restrição da soma dos inputs = 1
			self.constraints.append(self.solver.Constraint(1,1))
			for i in range(len(self.incoef)):
				self.constraints[len(self.constraints)-1].SetCoefficient(self.incoef[i],self.entries[dmu][i])
			resultado = self.solver.Solve()
			resposta.append(dict())
			resposta[-1]['bias'] = self.bias.solution_value()
			for i in range(len(self.incoef)):
				resposta[-1]['i'+str(i)] = self.incoef[i].solution_value()
			for j in range(len(self.outcoef)):
				resposta[-1]['o'+str(j)] = self.outcoef[j].solution_value()
		return copy.deepcopy(resposta)

	def __bcc_input_dual(self)->list:
		resposta = []
		for dmu in range(len(self.entries)):
			#Definindo as variáveis
			self.lamb = []
			self.constraints = []
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			for i in range(len(self.entries)):
				self.lamb.append(self.solver.NumVar(0,self.solver.infinity(),'lamb'+str(i)))
			self.theta = self.solver.NumVar(0,self.solver.infinity(),'theta')
			#Definindo a função objetivo
			self.objective.SetCoefficient(self.theta,1)
			self.objective.SetMinimization()
			#Definindo as restrições
			#Restrição 1
			for i in range(len(self.entries[dmu])):
				self.constraints.append(self.solver.Constraint(self.out[dmu][i],self.solver.infinity()))
				for j in range(len(self.out)):
					self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],self.out[j][i])
			#Restrição 2
			for i in range(len(self.entries[dmu])):
				self.constraints.append(self.solver.Constraint(-self.solver.infinity(),0))
				self.constraints[len(self.constraints)-1].SetCoefficient(self.theta,-self.entries[dmu][i])
				for j in range(len(self.entries)):
					self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],self.entries[j][i])
			#Restrição 3
			self.constraints.append(self.solver.Constraint(1,1))
			for j in range(len(self.entries)):
				self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],1)
			resultado = self.solver.Solve()
			resposta.append(dict())
			for i in range(len(self.lamb)):
				resposta[-1]['lamb'+str(i).zfill(3)] = self.lamb[i].solution_value()
			resposta[-1]['theta'] = self.theta.solution_value()
		return copy.deepcopy(resposta)

	def __bcc_output_primal(self)->list:
		resposta = []
		for dmu in range(len(self.entries)):
			#Definindo as variáveis
			self.incoef = []
			self.outcoef = []
			self.constraints = []
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			for i in range(len(self.entries[0])):
				self.incoef.append(self.solver.NumVar(0,self.solver.infinity(),'v'+str(i)))
			for i in range(len(self.out[0])):
				self.outcoef.append(self.solver.NumVar(0,self.solver.infinity(),'u'+str(i)))
			self.bias = self.solver.NumVar(-self.solver.infinity(),self.solver.infinity(),'b')
			#Definindo a função objetivo
			for i in range(len(self.incoef)):
				self.objective.SetCoefficient(self.incoef[i],self.entries[dmu][i])
			self.objective.SetCoefficient(self.bias,1)
			self.objective.SetMinimization()
			#Definindo as restrições
			#Restrição de que todos os valores devem ter inputs maiores que outputs
			for i in range(len(self.entries)):
				self.constraints.append(self.solver.Constraint(-self.solver.infinity(),0))
				self.constraints[i].SetCoefficient(self.bias,-1)
				for j in range(len(self.incoef)):
					self.constraints[i].SetCoefficient(self.incoef[j],-1*self.entries[i][j])
				for k in range(len(self.outcoef)):
					self.constraints[i].SetCoefficient(self.outcoef[k],self.out[i][k])
			#Restrição da soma dos inputs = 1
			self.constraints.append(self.solver.Constraint(1,1))
			for i in range(len(self.outcoef)):
				self.constraints[len(self.constraints)-1].SetCoefficient(self.outcoef[i],self.out[dmu][i])
			resultado = self.solver.Solve()
			resposta.append(dict())
			resposta[-1]['bias'] = self.bias.solution_value()
			for i in range(len(self.incoef)):
				resposta[-1]['i'+str(i)] = self.incoef[i].solution_value()
			for j in range(len(self.outcoef)):
				resposta[-1]['o'+str(j)] = self.outcoef[j].solution_value()
		return copy.deepcopy(resposta)

	def __bcc_output_dual(self)->list:
		resposta = []
		for dmu in range(len(self.entries)):
			#Definindo as variáveis
			self.lamb = []
			self.constraints = []
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			for i in range(len(self.entries)):
				self.lamb.append(self.solver.NumVar(0,self.solver.infinity(),'lamb'+str(i)))
			self.theta = self.solver.NumVar(0,self.solver.infinity(),'theta')
			#Definindo a função objetivo
			self.objective.SetCoefficient(self.theta,1)
			self.objective.SetMaximization()
			#Definindo as restrições
			#Restrição amarra o valor dos inputs
			for i in range(len(self.entries[dmu])):
				self.constraints.append(self.solver.Constraint(-self.solver.infinity(),self.entries[dmu][i]))
				for j in range(len(self.entries)):
					self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],self.entries[j][i])
			for i in range(len(self.out[dmu])):
				self.constraints.append(self.solver.Constraint(0,self.solver.infinity()))
				self.constraints[len(self.constraints)-1].SetCoefficient(self.theta,-self.out[dmu][i])
				for j in range(len(self.out)):
					self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],self.out[j][i])
			self.constraints.append(self.solver.Constraint(1,1))
			for j in range(len(self.entries)):
				self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],1)
			resultado = self.solver.Solve()
			resposta.append(dict())
			for i in range(len(self.lamb)):
				resposta[-1]['lamb'+str(i).zfill(3)] = self.lamb[i].solution_value()
			resposta[-1]['theta'] = self.theta.solution_value()
		return copy.deepcopy(resposta)

	def __ccr_input_primal(self)->list:
		resposta = []
		for dmu in range(len(self.entries)):
			#Definindo as variáveis
			self.incoef = []
			self.outcoef = []
			self.constraints = []
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			for i in range(len(self.entries[0])):
				self.incoef.append(self.solver.NumVar(0,self.solver.infinity(),'v'+str(i)))
			for i in range(len(self.out[0])):
				self.outcoef.append(self.solver.NumVar(0,self.solver.infinity(),'u'+str(i)))
			#Definindo a função objetivo
			for i in range(len(self.outcoef)):
				self.objective.SetCoefficient(self.outcoef[i],self.out[dmu][i])
			self.objective.SetMaximization()
			#Definindo as restrições
			#Restrição de que todos os valores devem ter inputs maiores que outputs
			for i in range(len(self.entries)):
				self.constraints.append(self.solver.Constraint(-self.solver.infinity(),0))
				for j in range(len(self.incoef)):
					self.constraints[i].SetCoefficient(self.incoef[j],-1*self.entries[i][j])
				for k in range(len(self.outcoef)):
					self.constraints[i].SetCoefficient(self.outcoef[k],self.out[i][k])
			#Restrição da soma dos inputs = 1
			self.constraints.append(self.solver.Constraint(1,1))
			for i in range(len(self.incoef)):
				self.constraints[len(self.constraints)-1].SetCoefficient(self.incoef[i],self.entries[dmu][i])
			resultado = self.solver.Solve()
			resposta.append(dict())
			for i in range(len(self.incoef)):
				resposta[-1]['i'+str(i)] = self.incoef[i].solution_value()
			for j in range(len(self.outcoef)):
				resposta[-1]['o'+str(j)] = self.outcoef[j].solution_value()
		return copy.deepcopy(resposta)

	def __ccr_input_dual(self)->list:
		resposta = []
		bench = []
		for dmu in range(len(self.entries)):
			#Definindo as variáveis
			self.lamb = []
			self.constraints = []
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			for i in range(len(self.entries)):
				self.lamb.append(self.solver.NumVar(0,self.solver.infinity(),'lamb'+str(i)))
			self.theta = self.solver.NumVar(0,self.solver.infinity(),'theta')
			#Definindo a função objetivo
			self.objective.SetCoefficient(self.theta,1)
			self.objective.SetMinimization()
			#Definindo as restrições
			#Restrição amarra o valor dos inputs
			for i in range(len(self.entries[dmu])):
				self.constraints.append(self.solver.Constraint(self.out[dmu][i],self.solver.infinity()))
				for j in range(len(self.out)):
					self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],self.out[j][i])
			for i in range(len(self.entries[dmu])):
				self.constraints.append(self.solver.Constraint(-self.solver.infinity(),0))
				self.constraints[len(self.constraints)-1].SetCoefficient(self.theta,-self.entries[dmu][i])
				for j in range(len(self.entries)):
					self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],self.entries[j][i])
			resultado = self.solver.Solve()
			resposta.append(dict())
			for i in range(len(self.lamb)):
				if self.lamb[i].solution_value()>0:
					if i not in bench:
						bench.append(i)
				resposta[-1]['lamb'+str(i).zfill(3)] = self.lamb[i].solution_value()
			resposta[-1]['theta'] = self.theta.solution_value()
		return  copy.deepcopy(resposta)

	def __ccr_output_primal(self)->list:
		resposta = []
		for dmu in range(len(self.entries)):
			#Definindo as variáveis
			self.incoef = []
			self.outcoef = []
			self.constraints = []
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			for i in range(len(self.entries[0])):
				self.incoef.append(self.solver.NumVar(0,self.solver.infinity(),'v'+str(i)))
			for i in range(len(self.out[0])):
				self.outcoef.append(self.solver.NumVar(0,self.solver.infinity(),'u'+str(i)))
			#Definindo a função objetivo
			for i in range(len(self.incoef)):
				self.objective.SetCoefficient(self.incoef[i],self.entries[dmu][i])
			self.objective.SetMinimization()
			#Definindo as restrições
			#Restrição de que todos os valores devem ter inputs maiores que outputs
			for i in range(len(self.entries)):
				self.constraints.append(self.solver.Constraint(-self.solver.infinity(),0))
				for j in range(len(self.incoef)):
					self.constraints[i].SetCoefficient(self.incoef[j],-1*self.entries[i][j])
				for k in range(len(self.outcoef)):
					self.constraints[i].SetCoefficient(self.outcoef[k],self.out[i][k])
			#Restrição da soma dos inputs = 1
			self.constraints.append(self.solver.Constraint(1,1))
			for i in range(len(self.outcoef)):
				self.constraints[len(self.constraints)-1].SetCoefficient(self.outcoef[i],self.out[dmu][i])
			resultado = self.solver.Solve()
			resposta.append(dict())
			for i in range(len(self.incoef)):
				resposta[-1]['i'+str(i)] = self.incoef[i].solution_value()
			for j in range(len(self.outcoef)):
				resposta[-1]['o'+str(j)] = self.outcoef[j].solution_value()
		return copy.deepcopy(resposta)

	def __ccr_output_dual(self)->list:
		resposta = []
		for dmu in range(len(self.entries)):
			#Definindo as variáveis
			self.lamb = []
			self.constraints = []
			self.solver = pywraplp.Solver('DEA',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
			self.objective = self.solver.Objective()
			for i in range(len(self.entries)):
				self.lamb.append(self.solver.NumVar(0,self.solver.infinity(),'lamb'+str(i)))
			self.theta = self.solver.NumVar(0,self.solver.infinity(),'theta')
			#Definindo a função objetivo
			self.objective.SetCoefficient(self.theta,1)
			self.objective.SetMaximization()
			#Definindo as restrições
			#Restrição amarra o valor dos inputs
			for i in range(len(self.entries[dmu])):
				self.constraints.append(self.solver.Constraint(-self.solver.infinity(),self.entries[dmu][i]))
				for j in range(len(self.entries)):
					self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],self.entries[j][i])
			for i in range(len(self.out[dmu])):
				self.constraints.append(self.solver.Constraint(0,self.solver.infinity()))
				self.constraints[len(self.constraints)-1].SetCoefficient(self.theta,-self.out[dmu][i])
				for j in range(len(self.out)):
					self.constraints[len(self.constraints)-1].SetCoefficient(self.lamb[j],self.out[j][i])
			resultado = self.solver.Solve()
			resposta.append(dict())
			for i in range(len(self.lamb)):
				resposta[-1]['lamb'+str(i).zfill(3)] = self.lamb[i].solution_value()
			resposta[-1]['theta'] = self.theta.solution_value()
		return  copy.deepcopy(resposta)

	def BCC(self,orientation:str='input',type:str='primal')->list:
		if type == 'primal':
			if orientation == 'input':
				return self.__bcc_input_primal()
			elif orientation == 'output':
				return self.__bcc_output_primal()
		elif type == 'dual':
			if orientation == 'input':
				return self.__bcc_input_dual()
			elif orientation == 'output':
				return self.__bcc_output_dual()

	def CCR(self,orientation:str='input',type:str='primal')->list:
		if type == 'primal':
			if orientation == 'input':
				return self.__ccr_input_primal()
			elif orientation == 'output':
				return self.__ccr_output_primal()
		elif type == 'dual':
			if orientation == 'input':
				return self.__ccr_input_dual()
			elif orientation == 'output':
				return self.__ccr_output_dual()
