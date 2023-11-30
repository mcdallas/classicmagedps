from classicmagedps import FireEnvironment, FireMage

env = FireEnvironment()

mage1 = FireMage(name='PepoT2', sp=914, crit=20.91, hit=16, fullt2=True)

env.add_mages([mage1])

mage1.smart_scorch()

env.run(until=200)
env.meter.report()
