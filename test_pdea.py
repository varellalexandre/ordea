from PDEA import *
def test_pdea():
	base = pd.read_excel("./modelos/modelo_sonia.xlsx")
	dea = PDEA("./modelos/new_model.json",base)
