import tellurium as te
import SimpleSEDML

r = te.loada("""
S1 -> S2; k1*S1
k1 = 0.4; S1 = 10
""")
m = r.simulate (0,50, 100)
#r.plot()
ss = SimpleSEDML.makeSingleModelTimeCourse(r.getSBML(), is_plot=False)
ss.execute()
