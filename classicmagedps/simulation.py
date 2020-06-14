from copy import deepcopy
from tqdm import trange
from collections import defaultdict
from classicmagedps.env import FireEnvironment
from classicmagedps.utils import mean


class Simulation:

    def __init__(self, env=FireEnvironment, mages=None, coe=True):
        self.env_class = env
        self.mages = mages or []
        self.coe = coe
        self.results = {
            'dps': defaultdict(list),
            'avg_mage_dps': [],
            'uptime': [],
            '5 stack uptime': [],
            'avg_tick': []
        }

    def run(self, iterations, duration):

        for _ in trange(iterations):
            env = self.env_class()
            env.debuffs.coe = self.coe
            env.PRINT = False
            mages = [deepcopy(mage) for mage in self.mages]
            env.add_mages(mages)

            env.run(until=duration)

            for mage, mdps in env.meter.dps().items():
                self.results['dps'][mage].append(mdps)
            self.results['avg_mage_dps'].append(env.meter.raid_dmg())
            self.results['uptime'].append(env.ignite.uptime)
            self.results['5 stack uptime'].append(env.ignite.uptime_5_stacks)
            self.results['avg_tick'].append(env.ignite.avg_tick)

        self.report()

    def report(self):
        for mage in self.results['dps']:
            print(f"{mage} average DPS : {mean(self.results['dps'][mage])}")

        print(f"Average mage dps: {mean(self.results['avg_mage_dps'])}")
        print(f"Average ignite uptime : {100 * mean(self.results['uptime'])}%")
        print(f"Average 5 stack ignite uptime : {100 * mean(self.results['5 stack uptime'])}%")
        print(f"Average ignite tick : {mean(self.results['avg_tick'])}")



