from classicmagedps import FireEnvironment, FireMage, Simulation

mage1 = FireMage(name='Alice', sp=500, crit=30, hit=12, fullt2=True)
mage2 = FireMage(name='Bob', sp=456, crit=22, hit=16)
mage3 = FireMage(name='Charlie', sp=525, crit=28, hit=9)
mage4 = FireMage(name='Duncan', sp=525, crit=28, hit=9)

mage1.one_scorch_one_pyro_then_fb()
mage2.spam_scorch()
mage3.spam_fireballs()
mage4.one_scorch_one_frostbolt_then_fb()

sim = Simulation(env=FireEnvironment, mages=[mage1, mage2, mage3, mage4])
sim.run(iterations=1000, duration=90)