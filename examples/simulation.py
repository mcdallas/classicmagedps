from classicmagedps import FireEnvironment, FireMage, ApFrostMage, Simulation, WcMage

mage1 = FireMage(name='PepoT2', sp=914, crit=20.91, hit=16, fullt2=True)
mage2 = FireMage(name='Pepo', sp=945, crit=28.34, hit=16, fullt2=False)


mage1.smart_scorch()
mage2.smart_scorch()


sim = Simulation(env=FireEnvironment, mages=[mage1, mage2])
sim.run(iterations=10000, duration=90)
