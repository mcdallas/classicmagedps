from classicmagedps import FireEnvironment, FireMage, ApFrostMage, Simulation, WcMage, FrostEnvironment

t2_mage = ApFrostMage(name='pepo_t2', sp=827, crit=23.72, hit=16, fullt2=True, haste=0)
reg_mage = ApFrostMage(name='pepo_reg', sp=892, crit=25.89, hit=16, fullt2=False, haste=0)

t2_mage.spam_frostbolts()
reg_mage.spam_frostbolts()

sim = Simulation(env=FrostEnvironment, mages=[t2_mage, reg_mage])
sim.run(iterations=1000, duration=200)
