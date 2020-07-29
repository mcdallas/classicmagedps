import simpy
import random
from classicmagedps.utils import DamageMeter


class FrostEnvironment(simpy.Environment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mages = []
        self.PRINT = True
        self.debuffs = Debuffs(self)
        self.meter = DamageMeter(self)
        self.process(self.debuffs.run())

    def time(self):
        dt = str(round(self.now, 1))
        return '[' + str(dt) + ']'

    def p(self, msg):
        if self.PRINT:
            print(msg)

    def add_mage(self, mage):
        self.mages.append(mage)
        mage.env = self

    def add_mages(self, mages):
        self.mages.extend(mages)
        for mage in mages:
            mage.env = self

    def run(self, *args, **kwargs):
        random.shuffle(self.mages)
        for mage in self.mages:
            self.process(mage.rotation(mage))
        super().run(*args, **kwargs)


class FireEnvironment(FrostEnvironment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ignite = Ignite(self)
        self.process(self.ignite.tick())


class Debuffs:

    def __init__(self, env, coe=True):
        self.env = env
        self.scorch_stacks = 0
        self.scorch_timer = 0
        self.coe = coe
        self.wc_stacks = 0
        self.wc_timer = 0

    def scorch(self):
        self.scorch_stacks = min(self.scorch_stacks + 1, 5)
        self.scorch_timer = 30

    def wc(self):
        self.wc_stacks = min(self.wc_stacks + 1, 5)
        self.wc_timer = 30

    def run(self):
        while True:
            yield self.env.timeout(1)
            self.scorch_timer = max(self.scorch_timer - 1, 0)
            if not self.scorch_timer:
                self.scorch_stacks = 0
            self.wc_timer = max(self.wc_stacks - 1, 0)
            if not self.wc_timer:
                self.wc_stacks = 0


class Ignite:

    def __init__(self, env):
        self.env = env
        self.cum_dmg = 0
        self.ticks_left = 0
        self.owner = None
        self.stacks = 0
        self._uptime = 0
        self._5_stack_uptime = 0
        self.ticks = []
        self.PI = False
        self.crit_this_window = False

    def refresh(self, mage, dmg):
        if not self.owner:
            self.owner = mage

        if self.stacks <= 4:
            self.cum_dmg += dmg
            self.stacks += 1
        if self.stacks == 1 and self.owner.pi.active:
            self.PI = True

        # existing ignite
        if self.active and not self.crit_this_window and self.ticks_left == 1:
            self.ticks_left += 1
            self.crit_this_window = True
        else:  # new ignite
            self.ticks_left = 2
            self.crit_this_window = True

    def _do_dmg(self):
        tick_dmg = self.cum_dmg * 0.2

        if self.env.debuffs.coe:
            tick_dmg *= 1.1  # ignite double dips on CoE

        if self.PI:
            tick_dmg *= 1.2

        tick_dmg *= 1 + self.env.debuffs.scorch_stacks * 0.03  # ignite double dips on imp.scorch
        if self.owner.dmf:
            tick_dmg *= 1.1  # ignite double dips on DMF

        tick_dmg = int(tick_dmg)
        self.env.p(f"{self.env.time()} - ({self.owner.name}) ignite ({self.stacks}) tick {tick_dmg} ")
        self.env.meter.register(self.owner, tick_dmg)
        self.ticks.append(tick_dmg)

    def drop(self):
        if self.stacks:
            self.owner.print(f"Ignite dropped")
        self.owner = None
        self.cum_dmg = 0
        self.stacks = 0
        self.PI = False
        self.ticks_left = 0

    def monitor(self):
        while True:
            if self.active:
                self._uptime += 0.1
                if self.stacks == 5:
                    self._5_stack_uptime += 0.1

            yield self.env.timeout(0.1)

    def tick(self):
        self.env.process(self.monitor())
        while True:
            if self.active:
                if self.ticks_left:
                    yield self.env.timeout(2)
                    self._do_dmg()
                    self.crit_this_window = False
                    self.ticks_left -= 1
                else:
                    self.drop()
            else:
                yield self.env.timeout(0.1)

    @property
    def active(self):
        return self.owner is not None

    @property
    def uptime(self):
        return self._uptime / self.env.now

    @property
    def uptime_5_stacks(self):
        return self._5_stack_uptime/self.env.now

    @property
    def avg_tick(self):
        return sum(self.ticks) / len(self.ticks)

    def report(self):
        print(f"Ignite uptime: {round(self.uptime * 100, 2)}%")
        print(f"5 stack ignite uptime: {round(self.uptime_5_stacks * 100, 2)}%")
        print(f"Average tick: {round(self.avg_tick, 2)}")