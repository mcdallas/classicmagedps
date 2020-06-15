# classicmagedps

Work in progress Simulation Framework for estimating Mage DPS for World of Warcraft classic.


## Installation

`$ pip install classicmagedps`

## Usage
<p align="center">
        <a href="https://repl.it/@mcdallas/CrowdedBowedLinuxpc"><img src="https://repl.it/badge/github/mcdallas/classicmagedps" align="center" /></a>
</p>
For a single iteration:

``` python
from classicmagedps import FireEnvironment, FireMage

# Instantiate the environment
env = FireEnvironment()

# Create as many Mages as you want
# crit is a mage's TOTAL crit including worldbuffs/gear/int/talents etc (but not debuffs like WC)
# hit is a mage's TOTAL +hit from gear and talents
mage1 = FireMage(name='Alice', sp=500, crit=30, hit=12, fullt2=True)
mage2 = FireMage(name='Bob', sp=456, crit=22, hit=16)
mage3 = FireMage(name='Charlie', sp=525, crit=28, hit=9)
mage4 = FireMage(name='Duncan', sp=525, crit=28, hit=9)
mage5 = FireMage(name='Eddie', sp=570, crit=33, hit=15)

env.add_mages([mage1, mage2, mage3, mage4, mage5])

# Select each mage's rotation, see below for a list of available rotations
mage1.one_scorch_one_pyro_then_fb()
mage2.one_scorch_one_frostbolt_then_fb()
mage3.spam_fireballs()
mage4.spam_scorch()
mage5.one_scorch_one_pyro_then_fb()

env.run(until=30)  # fight duration
env.meter.report()

```

You will get an output like this
```
[2.0] - (Bob) scorch 575
[2.1] - (Alice) scorch **864**
[2.1] - (Eddie) scorch 588
[2.9] - (Duncan) scorch RESIST
[3.4] - (Charlie) fireball **1998**
[4.1] - (Alice) ignite (2) tick 705 
[4.4] - (Duncan) scorch **952**
[4.5] - (Bob) frostbolt **1852**
[5.9] - (Duncan) scorch RESIST
[6.1] - (Alice) ignite (3) tick 964 
[6.4] - (Charlie) fireball 1498
[7.4] - (Duncan) scorch **1000**
[7.5] - (Bob) fireball 1458
[8.1] - (Alice) pyroblast 1671
[8.1] - (Alice) ignite (4) tick 1217 
[8.1] - (Eddie) pyroblast 1897
[8.9] - (Duncan) scorch 701
[9.4] - (Charlie) fireball **2490**
[10.1] - (Alice) ignite (5) tick 1847 
[10.4] - (Duncan) scorch 683
[10.5] - (Bob) fireball **2199**
[11.1] - (Alice) fireball **2235**
[11.1] - (Eddie) fireball 1696
[11.9] - (Duncan) scorch **1042**
[12.1] - (Alice) ignite (5) tick 1847 
[12.4] - (Charlie) fireball 1532
[13.4] - (Duncan) scorch 684
[13.5] - (Bob) fireball 1477
[14.1] - (Alice) fireball 1522
[14.1] - (Alice) T2 proc
[14.1] - (Alice) ignite (5) tick 1847 
[14.1] - (Eddie) fireball 1788
[14.9] - (Duncan) scorch **1000**
[15.4] - (Charlie) fireball 1664
[15.6] - (Alice) fireball **2520**
[16.1] - (Alice) ignite (5) tick 1847 
[16.4] - (Duncan) scorch **1032**
[16.5] - (Bob) fireball 1603
[17.1] - (Eddie) fireball **2661**
[17.9] - (Duncan) scorch **1048**
[18.1] - (Alice) ignite (5) tick 1847 
[18.4] - (Charlie) fireball 1724
[18.6] - (Alice) fireball 1568
[18.6] - (Alice) T2 proc
[19.4] - (Duncan) scorch **1008**
[19.5] - (Bob) fireball 1547
[20.1] - (Alice) fireball 1484
[20.1] - (Alice) ignite (5) tick 1847 
[20.1] - (Eddie) fireball 1726
[20.9] - (Duncan) scorch 701
[21.4] - (Charlie) fireball **2299**
[22.1] - (Alice) ignite (5) tick 1847 
[22.4] - (Duncan) scorch 691
[22.5] - (Bob) fireball 1459
[23.1] - (Alice) fireball 1505
[23.1] - (Eddie) fireball 1717
[23.9] - (Duncan) scorch **1030**
[24.1] - (Alice) ignite (5) tick 1847 
[24.4] - (Charlie) fireball 1547
[25.4] - (Duncan) scorch **994**
[25.5] - (Bob) fireball **2247**
[26.1] - (Alice) fireball **2224**
[26.1] - (Alice) ignite (5) tick 1847 
[26.1] - (Eddie) fireball 1740
[26.9] - (Duncan) scorch 673
[27.4] - (Charlie) fireball 1547
[27.6] - (Alice) scorch 643
[28.1] - (Alice) ignite (5) tick 1847 
[28.4] - (Duncan) scorch **973**
[28.5] - (Bob) fireball **2412**
[29.1] - (Eddie) fireball **2524**
[29.9] - (Duncan) scorch 670
[30.0] - (Bob) scorch 647
Bob - 582.5 dps
Alice - 1253.1 dps
Eddie - 544.6 dps
Duncan - 496.1 dps
Charlie - 543.3 dps
Average mage DPS : 683.9
Ignite uptime: 93.0%
Average tick: 1642.77
```

For multiple iterations:

``` python
from classicmagedps import FireEnvironment, FireMage, Simulation

# Create your mages, same as before
mage1 = FireMage(name='Alice', sp=500, crit=30, hit=12, fullt2=True)
mage2 = FireMage(name='Bob', sp=456, crit=22, hit=16)
mage3 = FireMage(name='Charlie', sp=525, crit=28, hit=9)
mage4 = FireMage(name='Duncan', sp=525, crit=28, hit=9)

# Set a rotation for each mage
mage1.one_scorch_one_pyro_then_fb()
mage2.spam_scorch()
mage3.spam_fireballs()
mage4.one_scorch_one_frostbolt_then_fb()

sim = Simulation(env=FireEnvironment, mages=[mage1, mage2, mage3, mage4])
sim.run(iterations=1000, duration=90)
```

After the simulation finishes the result will look like this:

```
Duncan average DPS : 716.37
Bob average DPS : 644.09
Alice average DPS : 790.85
Charlie average DPS : 733.51
Average mage dps: 721.21
Average ignite uptime : 88.0%
Average ignite tick : 1710.48
```


## What?

If you have no idea what I am talking about or how to install/run this, click the button bellow to run the code from the first example. Just change the parameters you want and click run.

<p align="center">
        <a href="https://repl.it/@mcdallas/CrowdedBowedLinuxpc"><img src="https://repl.it/badge/github/mcdallas/classicmagedps" align="center" /></a>
</p>

## Talents and Debuffs

You can customize each mage by passing additional arguments. The full constructor looks like this:
    
    
    def __init__(self,
                 name,
                 sp,
                 crit,
                 hit,
                 env=None,
                 firepower=True,
                 dmf=False,
                 imp_scorch=True,
                 incineration=False,
                 wc=False,
                 ai=False,
                 piercing_ice=True,
                 fullt2=False
                 ): 
                 
 
the FireMage, APFrostMage and WCMage subclasses assume reasonable defaults regarding talents.
    
Every simulation assumes Curse of Elements is applied, you can turn it off by adding this line after you create your env
```
env.debuffs.coe = False
```
or by passing it as an argument in Simulation
```
sim = Simulation(env=FireEnvironment, coe=False, mages=[mage1, mage2, mage3, mage4])
```
no consumables are assumed otherwise, you need to factor those in your total sp/crit


## Rotations
All rotations include a random initial delay of 0-2 seconds. You can disable this by passing the delay=0 parameter

The full list of currently supported rotations is:


* spam_scorch()

* spam_fireballs()

* spam_frostbolts()

1 scorch + 9 fireballs (repeated)
* one_scorch_then_fireballs()  

 1 scorch + 1 pyro + 6 fireballs (repeated)
* one_scorch_one_pyro_then_fb() 

1 scorch + 1 frostbolt + 8 fireballs (repeated)
* one_scorch_one_frostbolt_then_fb()  

 cast scorch if less than 5 imp.scorch stacks 
 or if 5 ignite stacks (to keep it rolling) else cast fireball
* smart_scorch()  


You can pass as arguments to each rotation when you want each mage to attempt
to activate their cooldowns. For example `mage1.spam_frostbolts(ap=20, pi=30)` will
tell the first mage to attempt to activate AP at the 20th second of the fight and 
Power infusion at the 30th second

Available cooldowns are: ap, pi, toep, combustion, mqg
