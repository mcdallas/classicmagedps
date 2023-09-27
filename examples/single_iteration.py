from classicmagedps import FireEnvironment, FireMage

env = FireEnvironment()

mage1 = FireMage(name='Alice', sp=500, crit=30, hit=12)
mage2 = FireMage(name='Bob', sp=456, crit=30, hit=12)
mage3 = FireMage(name='Charlie', sp=525, crit=30, hit=12)
mage4 = FireMage(name='Duncan', sp=525, crit=30, hit=12)
mage5 = FireMage(name='Eddie', sp=570, crit=30, hit=12)

env.add_mages([mage1, mage2, mage3, mage4, mage5])

mage1.spam_scorch()
mage2.spam_scorch()
mage3.spam_scorch()
mage4.spam_scorch()
mage5.spam_scorch()

env.run(until=30)
env.meter.report()
