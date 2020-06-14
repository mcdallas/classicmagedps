from classicmagedps import FrostEnvironment, ApFrostMage, WcMage

env = FrostEnvironment()

alice = ApFrostMage(name='Alice', sp=500, crit=30, hit=12, fullt2=True)
bob = WcMage(name='Bob', sp=456, crit=22, hit=16)
charlie = ApFrostMage(name='Charlie', sp=525, crit=28, hit=9)
duncan = ApFrostMage(name='Duncan', sp=525, crit=28, hit=9)
eddie = ApFrostMage(name='Eddie', sp=570, crit=33, hit=15)

env.add_mages([alice, bob, charlie, duncan, eddie])

alice.spam_frostbolts(ap=0, mqg=0)
bob.spam_frostbolts()
charlie.spam_frostbolts(ap=15)
duncan.spam_frostbolts(ap=15)
eddie.spam_frostbolts(ap=15)

env.run(until=60)
env.meter.report()
