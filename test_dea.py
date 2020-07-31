from DEA import *
def test_dea():
	inp = [
		[20,151],
		[19,131],
		[25,160],
		[20,168],
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
		[149,56],
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
	pd.DataFrame(dea.CCR(orientation='output')).to_excel(writer,'CCR OUTPUT')
	pd.DataFrame(dea.CCR(orientation='input')).to_excel(writer,'CCR INPUT')
	pd.DataFrame(dea.CCR(orientation='input',type='dual')).to_excel(writer,'CCR INPUT DUAL')
	pd.DataFrame(dea.CCR(orientation='output',type='dual')).to_excel(writer,'CCR OUTPUT DUAL')
	pd.DataFrame(dea.BCC(orientation='output')).to_excel(writer,'BCC OUTPUT')
	pd.DataFrame(dea.BCC(orientation='input')).to_excel(writer,'BCC INPUT')
	pd.DataFrame(dea.BCC(orientation='output',type='dual')).to_excel(writer,'BCC OUTPUT DUAL')
	pd.DataFrame(dea.BCC(orientation='input',type='dual')).to_excel(writer,'BCC INPUT DUAL')
	writer.save()
