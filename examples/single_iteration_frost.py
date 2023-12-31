from classicmagedps import FrostEnvironment, ApFrostMage, WcMage

env = FrostEnvironment()

reg_mage1 = ApFrostMage(name='mage1', sp=945, crit=30, hit=16, fullt2=True, haste=0)

reg_mage1.spam_frostbolts(arcane_power=20, mqg=20, presence_of_mind=20)

env.add_mages([reg_mage1])

env.run(until=100)
env.meter.report()
