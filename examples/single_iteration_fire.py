from classicmagedps import FireEnvironment, FireMage

env = FireEnvironment()

reg_mage1 = FireMage(name='mage1', sp=945, crit=30, hit=16, fullt2=True, haste=0, lag=0)

reg_mage1.smart_scorch(combustion=20, mqg=20)

env.add_mages([reg_mage1])

env.run(until=50)
env.meter.report()
