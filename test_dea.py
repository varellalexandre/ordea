from DEA import *
def test_dea():
	inp = [
		[20,151],
		[19,131],
		[25,160],
		[27,168],
		[22,158],
		[55,255],
		[33,235],
		[31,206],
		[30,244],
		[50,268],
		[53,306],
		[38,284]
	]
	out = [
		[100,90],
		[150,50],
		[160,55],
		[180,72],
		[94,66],
		[230,90],
		[220,88],
		[152,80],
		[290,100],
		[250,100],
		[262,147],
		[250,120]
	]
	dea = DEA(inp,out)
	writer = pd.ExcelWriter('resposta.xlsx')
	dea.CCR(orientation='output').to_excel(writer,'CCR OUTPUT')
	dea.CCR(orientation='input').to_excel(writer,'CCR INPUT')
	dea.CCR(orientation='input',type='dual').to_excel(writer,'CCR INPUT DUAL')
	dea.CCR(orientation='output',type='dual').to_excel(writer,'CCR OUTPUT DUAL')
	dea.BCC(orientation='output').to_excel(writer,'BCC OUTPUT')
	dea.BCC(orientation='input').to_excel(writer,'BCC INPUT')
	dea.BCC(orientation='output',type='dual').to_excel(writer,'BCC OUTPUT DUAL')
	dea.BCC(orientation='input',type='dual').to_excel(writer,'BCC INPUT DUAL')
	writer.save()
		