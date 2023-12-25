from classicmagedps import FireEnvironment, FireMage, ApFrostMage, Simulation, WcMage

t2_mage = FireMage(name='pepo_t2', sp=939, crit=26.84, hit=15, fullt2=True)
reg_mage = FireMage(name='pepo_reg', sp=953, crit=29.13, hit=16, fullt2=False)

t2_mage.smart_scorch()
reg_mage.smart_scorch()

sim = Simulation(env=FireEnvironment, mages=[t2_mage, reg_mage])
sim.run(iterations=2500, duration=200)
