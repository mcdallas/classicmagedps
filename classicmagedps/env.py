import simpy
import random
from classicmagedps.utils import DamageMeter


class FrostEnvironment(simpy.Environment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mages = []
        self.PRINT = True
        self.total_spell_dmg = 0
        self.total_ignite_dmg = 0
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


class FireballDot:
    def __init__(self, owner):
        self.owner = owner
        self.timer = 8

    def tick_dmg(self):
        dmg = 19
        dmg *= 1 + self.owner.env.debuffs.scorch_stacks * 0.03
        return round(dmg)


class PyroblastDot:
    def __init__(self, owner, sp):
        self.owner = owner
        self.sp = sp
        self.timer = 12

    def tick_dmg(self):
        dmg = 15 + self.sp * 0.15  # what it seems to be on turtle
        dmg *= 1 + self.owner.env.debuffs.scorch_stacks * 0.03
        return round(dmg)


class Debuffs:
    def __init__(self, env, coe=True):
        self.env = env
        self.scorch_stacks = 0
        self.scorch_timer = 0
        self.coe = coe
        self.winters_chill_stacks = 0
        self.winters_chill_timer = 0

        self.fireball_dots = []
        self.pyroblast_dots = []

    def scorch(self):
        self.scorch_stacks = min(self.scorch_stacks + 1, 5)
        self.scorch_timer = 30

    def winters_chill(self):
        self.winters_chill_stacks = min(self.winters_chill_stacks + 1, 5)
        self.winters_chill_timer = 30

    def fireball_dot(self, owner):
        # check if dot already exists
        for dot in self.fireball_dots:
            if dot.owner == owner:
                dot.timer = 8
                return

        self.fireball_dots.append(FireballDot(owner))


    def pyroblast_dot(self, owner, sp):
        # check if dot already exists
        for dot in self.pyroblast_dots:
            if dot.owner == owner:
                dot.timer = 12
                dot.sp = sp
                return

        self.pyroblast_dots.append(PyroblastDot(owner, sp))

    def run(self):
        while True:
            yield self.env.timeout(1)
            self.scorch_timer = max(self.scorch_timer - 1, 0)
            if not self.scorch_timer:
                self.scorch_stacks = 0
            self.winters_chill_timer = max(self.winters_chill_stacks - 1, 0)
            if not self.winters_chill_timer:
                self.winters_chill_stacks = 0

            # check for fireball dots
            for dot in self.fireball_dots:
                dot.timer -= 1
                if dot.timer % 2 == 0:
                    # self.env.p(
                    #     f"{self.env.time()} - ({dot.owner.name}) fireball tick {dot.tick_dmg()} time remaining {dot.timer}")
                    self.env.meter.register(dot.owner, dot.tick_dmg())
                if dot.timer <= 0:
                    self.fireball_dots.remove(dot)

            # check for pyroblast dots
            for dot in self.pyroblast_dots:
                dot.timer -= 1
                if dot.timer % 3 == 0:
                    self.env.p(
                        f"{self.env.time()} - ({dot.owner.name}) pyroblast tick {dot.tick_dmg()} time remaining {dot.timer}")
                    self.env.meter.register(dot.owner, dot.tick_dmg())
                if dot.timer <= 0:
                    self.pyroblast_dots.remove(dot)


class Ignite:

    def __init__(self, env):
        self.env = env
        self.cum_dmg = 0
        self.ticks_left = 0
        self.owner = None
        self.stacks = 0
        self._uptime = 0
        self._3_stack_uptime = 0
        self._5_stack_uptime = 0
        self.ticks = []
        self.PI = False
        self.crit_this_window = False

    def refresh(self, mage, dmg):
        if not self.owner:
            self.owner = mage

        single_stack_extend = self.stacks == 1 and self.ticks_left == 2
        multi_stack_extend = self.stacks > 1 and self.ticks_left >= 1

        # self.env.p(
        #     f"Ignite refresh ticks left {self.ticks_left} stacks={self.stacks} single={single_stack_extend} multi={multi_stack_extend}")

        # existing ignite
        if self.active and (single_stack_extend or multi_stack_extend):
            if self.stacks <= 4:
                self.cum_dmg += dmg
                self.stacks += 1
            if self.owner.power_infusion.active:
                self.PI = True

            self.ticks_left = 2
            self.crit_this_window = True

            # self.env.p(f"Ignite refresh extend ticks left {self.ticks_left}")
        else:  # new ignite
            self.cum_dmg = dmg
            self.stacks = 1
            self.owner = mage
            self.ticks_left = 3
            self.crit_this_window = True
            # self.env.p(f"New ignite ticks left {self.ticks_left}")

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
        self.env.p(
            f"{self.env.time()} - ({self.owner.name}) ({self.stacks}) ignite tick {tick_dmg} ticks remaining {self.ticks_left}")
        self.env.meter.register(self.owner, tick_dmg)
        self.env.total_ignite_dmg += tick_dmg
        self.ticks.append(tick_dmg)

    def drop(self):
        if self.stacks:
            self.owner.print(f"Ignite dropped")
        self.owner = None
        self.cum_dmg = 0
        self.stacks = 0
        self.PI = False
        self.ticks_left = 0
        self.crit_this_window = False

    def monitor(self):
        while True:
            if self.active:
                self._uptime += 0.05
                if self.stacks >= 3:
                    self._3_stack_uptime += 0.05
                if self.stacks == 5:
                    self._5_stack_uptime += 0.05

            yield self.env.timeout(0.05)

    def tick(self):
        self.env.process(self.monitor())
        while True:
            if self.active:
                # process ignite tick
                if self.ticks_left:
                    self.ticks_left -= 1
                    self._do_dmg()
                    self.crit_this_window = False

                    if self.ticks_left == 0:
                        self.drop()
                    else:
                        # first ignite detected after .05 seconds but ticks immediately
                        # so account for that in yield
                        yield self.env.timeout(2) if self.stacks == 1 else self.env.timeout(1.95)
            else:
                yield self.env.timeout(0.05)

    @property
    def active(self):
        return self.owner is not None

    @property
    def uptime(self):
        return self._uptime / self.env.now

    @property
    def uptime_gte_3_stacks(self):
        return self._3_stack_uptime / self.env.now

    @property
    def uptime_5_stacks(self):
        return self._5_stack_uptime / self.env.now

    @property
    def avg_tick(self):
        if not self.ticks:
            return 0
        return sum(self.ticks) / len(self.ticks)

    def report(self):
        print(f"Ignite uptime: {round(self.uptime * 100, 2)}%")
        print(f">=3 stack ignite uptime: {round(self.uptime_gte_3_stacks * 100, 2)}%")
        print(f"5 stack ignite uptime: {round(self.uptime_5_stacks * 100, 2)}%")
        print(f"Average tick: {round(self.avg_tick, 2)}")
