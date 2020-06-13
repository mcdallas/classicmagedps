from classicmagedps import FireEnvironment, FireMage

env = FireEnvironment()

mage1 = FireMage(env, 'Alice', sp=500, crit=30, hit=12, fullt2=True)
mage2 = FireMage(env, 'Bob', sp=456, crit=22, hit=16)
mage3 = FireMage(env, 'Charlie', sp=525, crit=28, hit=9)
mage4 = FireMage(env, 'Duncan', sp=525, crit=28, hit=9)

mage1.one_scorch_one_pyro_then_fb()
mage2.one_scorch_one_pyro_then_fb()
mage3.one_scorch_one_pyro_then_fb()
mage4.one_scorch_one_pyro_then_fb()

env.run(until=60)
env.meter.report()
