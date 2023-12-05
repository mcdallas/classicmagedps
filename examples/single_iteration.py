from classicmagedps import FireEnvironment, FireMage

env = FireEnvironment()

reg_mage1 = FireMage(name='mage1', sp=945, crit=30, hit=16, fullt2=False)
reg_mage2 = FireMage(name='mage2', sp=945, crit=30, hit=16, fullt2=False)
reg_mage3 = FireMage(name='mage3', sp=945, crit=30, hit=16, fullt2=False)
reg_mage4 = FireMage(name='mage4', sp=945, crit=30, hit=16, fullt2=False)

reg_mage1.smart_scorch_and_fireblast()
reg_mage2.smart_scorch_and_fireblast()
reg_mage3.smart_scorch_and_fireblast()
reg_mage4.smart_scorch_and_fireblast()

env.add_mages([reg_mage1, reg_mage2, reg_mage3, reg_mage4])

env.run(until=200)
env.meter.report()
