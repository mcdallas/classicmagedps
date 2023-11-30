from classicmagedps import FireEnvironment, FireMage, ApFrostMage, Simulation, WcMage

t2_mage = FireMage(name='t2_mage', sp=914, crit=20.91, hit=16, fullt2=True)
reg_mage = FireMage(name='reg_mage', sp=945, crit=28.34, hit=16, fullt2=False)

t2_mage.smart_scorch()
reg_mage.smart_scorch()

sim = Simulation(env=FireEnvironment, mages=[t2_mage])
sim.run(iterations=5000, duration=200)

sim = Simulation(env=FireEnvironment, mages=[reg_mage])
sim.run(iterations=5000, duration=200)
