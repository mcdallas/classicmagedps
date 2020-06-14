from classicmagedps import FireEnvironment, FireMage

env = FireEnvironment()

mage1 = FireMage(name='Alice', sp=500, crit=30, hit=12)
mage2 = FireMage(name='Bob', sp=456, crit=22, hit=16)
mage3 = FireMage(name='Charlie', sp=525, crit=28, hit=9)
mage4 = FireMage(name='Duncan', sp=525, crit=28, hit=9)

env.add_mages([mage1, mage2, mage3, mage4])

mage1.one_scorch_one_pyro_then_fb(ap=5, pi=6, mqg=7)
mage2.one_scorch_one_pyro_then_fb(combustion=10, mqg=10)
mage3.one_scorch_one_pyro_then_fb()
mage4.one_scorch_one_pyro_then_fb()

env.run(until=60)
env.meter.report()
