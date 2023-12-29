from classicmagedps import FireEnvironment, FireMage, ApFrostMage, Simulation, WcMage

t2_mage = FireMage(name='pepo_t2', sp=917, crit=26.84, hit=16, fullt2=True, haste=0)
reg_mage = FireMage(name='pepo_reg', sp=940, crit=30.08, hit=16, fullt2=False, haste=0)

t2_mage.spam_fireballs()
reg_mage.spam_fireballs()

sim = Simulation(env=FireEnvironment, mages=[t2_mage, reg_mage])
sim.run(iterations=1000, duration=200)
