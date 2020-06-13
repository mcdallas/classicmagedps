from classicmagedps import FireEnvironment, FireMage

env = FireEnvironment()

mage1 = FireMage(name='Alice', sp=500, crit=30, hit=12, fullt2=True)
mage2 = FireMage(name='Bob', sp=456, crit=22, hit=16)
mage3 = FireMage(name='Charlie', sp=525, crit=28, hit=9)
mage4 = FireMage(name='Duncan', sp=525, crit=28, hit=9)
mage5 = FireMage(name='Eddie', sp=570, crit=33, hit=15)

env.add_mages([mage1, mage2, mage3, mage4, mage5])

mage1.one_scorch_one_pyro_then_fb()
mage2.one_scorch_one_frostbolt_then_fb()
mage3.spam_fireballs()
mage4.spam_scorch()
mage5.one_scorch_one_pyro_then_fb()

env.run(until=30)
env.meter.report()
