import simpy
import random

class Mage:

    def __init__(self,
                 env,
                 name,
                 sp,
                 crit,
                 hit,
                 firepower=True,
                 dmf=False,
                 imp_scorch=True,
                 incineration=False,
                 wc=False,
                 ai=False,
                 piercing_ice=True,
                 fullt2=False
                 ):
        self.env = env
        self.name = name
        self.sp = sp
        self.crit = crit
        self.hit = hit
        self.firepower = firepower
        self.dmf = dmf
        self.imp_scorch = imp_scorch
        self.incineration = incineration
        self.dmg_modifier = 1
        self.casting_time_modifier = 1
        self.wc = wc
        self.ai = ai
        self.piercing_ice = piercing_ice
        self.fullt2 = fullt2
        self._t2proc = False

    def _random_delay(self, secs=2):
        if secs:
            delay = round(random.random() * secs, 2)
            yield self.env.timeout(delay)

    def _spam_fireballs(self, delay=2):
        yield from self._random_delay(delay)

        while True:
            yield from self.fireball()

    def spam_fireballs(self, *args, **kwargs):
        self.env.process(self._spam_fireballs(*args, **kwargs))

    def _spam_frostbolts(self, delay=2):
        yield from self._random_delay(delay)

        while True:
            yield from self.frostbolt()

    def spam_frostbolts(self, *args, **kwargs):
        self.env.process(self._spam_fireballs(*args, **kwargs))

    def _spam_scorch(self, delay=2):
        yield from self._random_delay(delay)
        while True:
            yield from self.scorch()

    def spam_scorch(self, *args, **kwargs):
        self.env.process(self._spam_scorch(*args, **kwargs))

    def _one_scorch_then_fireballs(self, delay=2):
        """1 scorch then 9 fireballs rotation"""
        yield from self._random_delay(delay)

        while True:
            yield from self.scorch()
            for _ in range(9):
                yield from self.fireball()

    def one_scorch_then_fireballs(self, *args, **kwargs):
        self.env.process(self._one_scorch_then_fireballs(*args, **kwargs))

    def _one_pyro_one_scorch_then_fb(self, delay=1):
        yield from self._random_delay(delay)

        yield from self.pyroblast()
        yield from self.scorch()
        for _ in range(6):
            yield from self.fireball()

        yield from self._one_scorch_then_fireballs(delay=0)

    def one_pyro_one_scorch_then_fb(self, *args, **kwargs):
        self.env.process(self._one_pyro_one_scorch_then_fb(*args, **kwargs))

    def _one_scorch_one_pyro_then_fb(self, delay=1):
        yield from self._random_delay(delay)

        yield from self.scorch()
        yield from self.pyroblast()
        for _ in range(7):
            yield from self.fireball()

        yield from self._one_scorch_then_fireballs(delay=0)

    def one_scorch_one_pyro_then_fb(self, *args, **kwargs):
        self.env.process(self._one_scorch_one_pyro_then_fb(*args, **kwargs))

    def one_scorch_one_frostbolt_then_fb(self, delay=1):
        yield from self._random_delay(delay)

        yield from self.scorch()
        yield from self.frostbolt()
        for _ in range(8):
            yield from self.fireball()

        yield from self._one_scorch_then_fireballs(delay=0)

    def print(self, msg):
        self.env.p(f"{self.env.time()} - ({self.name}) {msg}")

    def fireball(self):
        min_dmg = 561
        max_dmg = 715
        casting_time = 3

        yield from self._fire_spell(name='fireball', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time)

    def _fire_spell(self, name, min_dmg, max_dmg, casting_time, crit_modifier=0):

        casting_time *= self.casting_time_modifier
        if self._t2proc:
            casting_time = 1.5
            self._t2proc = False
            self.print("T2 proc")

        hit_chance = min(83 + self.hit, 99)
        hit = random.randint(1, 100) <= hit_chance

        crit = random.randint(1, 100) <= self.crit + crit_modifier

        dmg = random.randint(min_dmg, max_dmg)
        coeff = min(casting_time / 3.5, 1) if not name == 'fireball' else 1
        dmg += self.sp * coeff

        if self.firepower:
            dmg *= 1.1  # Fire Power
        if self.ai:
            dmg *= 1.03
        if self.env.debuffs.coe:
            dmg *= 1.1  # CoE
        if self.dmf:
            dmg *= 1.1

        dmg *= 1 + self.env.debuffs.scorch_stacks * 0.03  # imp. scorch

        dmg = int(dmg * self.dmg_modifier)
        yield self.env.timeout(casting_time)

        if not hit:
            dmg = 0
            self.print(f"{name} RESIST")
        elif not crit:
            self.print(f"{name} {dmg}")

        else:

            dmg = int(dmg * 1.5)
            self.print(f"{name} **{dmg}**")
            self.env.ignite.refresh(self, dmg)

        if name == 'scorch' and self.imp_scorch:
            self.env.debuffs.scorch()

        self.env.meter.register(self, dmg)
        if self.fullt2 and name == 'fireball':
            if random.randint(1, 100) <= 10:
                self._t2proc = True

    def _frost_spell(self, name, min_dmg, max_dmg, casting_time):
        casting_time *= self.casting_time_modifier
        if self._t2proc:
            casting_time = 1.5
            self._t2proc = False
            self.print("T2 proc")

        hit_chance = min(83 + self.hit, 99)
        hit = random.randint(1, 100) <= hit_chance

        crit_chance = self.crit + self.env.debuffs.wc_stacks * 2
        crit = random.randint(1, 100) <= crit_chance

        dmg = random.randint(min_dmg, max_dmg)
        coeff = min(casting_time / 3.5, 1) if not name == 'frostbolt' else 6 / 7
        dmg += self.sp * coeff

        if self.piercing_ice:
            dmg *= 1.06  # Piercing Ice
        if self.ai:
            dmg *= 1.03
        if self.env.debuffs.coe:
            dmg *= 1.1  # CoE
        if self.dmf:
            dmg *= 1.1

        dmg = int(dmg * self.dmg_modifier)
        yield self.env.timeout(casting_time)

        if not hit:
            dmg = 0
            self.print(f"{name} RESIST")
        elif not crit:
            self.print(f"{name} {dmg}")

        else:
            dmg = int(dmg * 2)
            self.print(f"{name} **{dmg}**")

        if self.wc:
            self.env.debuffs.wc()

        self.env.meter.register(self, dmg)
        if self.fullt2 and name == 'frostbolt':
            if random.randint(1, 100) <= 10:
                self._t2proc = True

    def scorch(self):
        min_dmg = 237
        max_dmg = 280
        casting_time = 1.5
        crit_modifier = 4 if self.incineration else 0

        yield from self._fire_spell(name='scorch', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time,
                                    crit_modifier=crit_modifier)

    def pyroblast(self):
        min_dmg = 716
        max_dmg = 890
        casting_time = 6

        yield from self._fire_spell(name='pyroblast', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time)

    def frostbolt(self):
        min_dmg = 440
        max_dmg = 475
        casting_time = 2.5

        yield from self._frost_spell(name='frostbolt', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time)

    def ap(self):
        self.dmg_modifier = 1.3
        self.print("AP")

        def callback(self):
            yield self.env.timeout(15)
            self.dmg_modifier = 1

        self.env.process(callback(self))


class FireMage(Mage):
    def __init__(self,
                 env,
                 name,
                 sp,
                 crit,
                 hit,
                 dmf=False,
                 fullt2=False
                 ):
        super().__init__(
            env=env,
            name=name,
            sp=sp,
            crit=crit,
            hit=hit,
            dmf=dmf,
            firepower=True,
            imp_scorch=True,
            incineration=True,
            wc=False,
            ai=False,
            piercing_ice=False,
            fullt2=fullt2
        )


class ApFrostMage(Mage):
    def __init__(self,
                 env,
                 name,
                 sp,
                 crit,
                 hit,
                 dmf=False,
                 **kwargs
                 ):
        super().__init__(
            env=env,
            name=name,
            sp=sp,
            crit=crit,
            hit=hit,
            dmf=dmf,
            firepower=False,
            imp_scorch=False,
            incineration=False,
            wc=False,
            ai=True,
            piercing_ice=True,
            **kwargs
        )

    def _ap_frostbolts(self, delay=2):
        yield from self._random_delay(delay)
        self.ap()
        while True:
            yield from self.frostbolt()

    def ap_frostbolts(self, *args, **kwargs):
        self.env.process(self._ap_frostbolts(*args, **kwargs))

    def _wait_ap_frostbolts(self, delay=2):
        yield from self._random_delay(delay)
        for _ in range(6):
            yield from self.frostbolt()
        self.ap()
        while True:
            yield from self.frostbolt()

    def wait_ap_frostbolts(self, *args, **kwargs):
        self.env.process(self._wait_ap_frostbolts(*args, **kwargs))


class WcMage(Mage):
    def __init__(self,
                 env,
                 name,
                 sp,
                 crit,
                 hit,
                 dmf=False,
                 **kwargs
                 ):
        super().__init__(
            env=env,
            name=name,
            sp=sp,
            crit=crit,
            hit=hit,
            dmf=dmf,
            firepower=False,
            imp_scorch=False,
            incineration=False,
            wc=True,
            ai=False,
            piercing_ice=True,
            **kwargs
        )
