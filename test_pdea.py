from PDEA import *
def test_pdea():
	lista_dmus_n3 = [6,7,13,14,16,17,21,22,23,25,32,34,36,38,42]
	lista_dmus = [True if (element+1) in lista_dmus_n3 else False for element in range(45)]
	base = pd.read_excel("./modelos/modelo_sonia.xlsx")
	dea = PDEA("./modelos/new_model.json",base[lista_dmus])
	solution = dea.solve()
	pd.DataFrame(solution).to_excel('resultado_sonia.xlsx')