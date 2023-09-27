from classicmagedps import FireEnvironment, FireMage, ApFrostMage, Simulation, WcMage

mage1 = WcMage(name='Pepo', sp=664, crit=17, hit=12)
mage2 = ApFrostMage(name='Guy', sp=664, crit=17, hit=12)
mage3 = FireMage(name='Elsaf', sp=664, crit=17, hit=12)

mage1.spam_frostbolts()
mage2.spam_frostbolts()
mage3.smart_scorch()

sim = Simulation(env=FireEnvironment, mages=[mage1, mage2, mage3])
sim.run(iterations=5000, duration=90)
