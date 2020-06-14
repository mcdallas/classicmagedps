import random
from functools import partial


class Mage:

    ROTATIONS = [
        'spam_fireballs',
        'spam_scorch',
        'spam_frostbolts',
        'smart_scorch',
        'one_scorch_then_fireballs',
        'one_scorch_one_pyro_then_fb',
        'one_scorch_one_frostbolt_then_fb'
    ]

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
        self.sp_bonus = 0
        self.combustion = Combustion(self)
        self.ap = AP(self)
        self.pi = PI(self)
        self.toep = TOEP(self)
        self.mqg = MQG(self)

        if self.env:
            self.env.mages.append(self)

    def _random_delay(self, secs=2):
        if secs:
            delay = round(random.random() * secs, 2)
            yield self.env.timeout(delay)

    def _use_cds(self, **kwargs):
        for name, time in kwargs.items():
            cd = getattr(self, name)
            if cd.usable and self.env.now >= time:
                cd.activate()

    def _spam_fireballs(self, delay=2, **cds):
        yield from self._random_delay(delay)

        while True:
            self._use_cds(**cds)
            yield from self.fireball()

    def _spam_frostbolts(self, delay=2, **cds):
        yield from self._random_delay(delay)

        while True:
            self._use_cds(**cds)
            yield from self.frostbolt()

    def _spam_scorch(self, delay=2, **cds):
        yield from self._random_delay(delay)

        while True:
            self._use_cds(**cds)
            yield from self.scorch()

    def _one_scorch_then_fireballs(self, delay=2, **cds):
        """1 scorch then 9 fireballs rotation"""
        yield from self._random_delay(delay)

        while True:
            self._use_cds(**cds)
            yield from self.scorch()
            for _ in range(9):
                self._use_cds(**cds)
                yield from self.fireball()

    def _smart_scorch(self, delay=2, **cds):
        """Cast scorch if less than 5 imp scorch stacks or if 5 stack ignite (to keep it rolling) else cast fireball"""
        yield from self._random_delay(delay)
        while True:
            self._use_cds(**cds)
            if self.env.debuffs.scorch_stacks < 5 or (self.env.ignite.stacks == 5 and self.env.ignite.time_left > 1.5):
                yield from self.scorch()
            else:
                yield from self.fireball()

    def _one_scorch_one_pyro_then_fb(self, delay=1, **cds):
        yield from self._random_delay(delay)

        self._use_cds(**cds)
        yield from self.scorch()
        self._use_cds(**cds)
        yield from self.pyroblast()
        for _ in range(7):
            self._use_cds(**cds)
            yield from self.fireball()

        yield from self._one_scorch_then_fireballs(delay=0, **cds)

    def _rotationgetter(self, name, *args, **kwargs):
        def callback(mage):
            rotation = getattr(mage, '_' + name)
            return rotation(*args, **kwargs)
        self.rotation = callback

    def __getattr__(self, name):
        if name not in self.ROTATIONS:
            return self.__getattribute__(name)

        return partial(self._rotationgetter, name=name)

    def _one_scorch_one_frostbolt_then_fb(self, delay=1, **cds):
        yield from self._random_delay(delay)

        self._use_cds(**cds)
        yield from self.scorch()
        self._use_cds(**cds)
        yield from self.frostbolt()
        for _ in range(8):
            self._use_cds(**cds)
            yield from self.fireball()

        yield from self._one_scorch_then_fireballs(delay=0, **cds)

    def print(self, msg):
        self.env.p(f"{self.env.time()} - ({self.name}) {msg}")

    def fireball(self):
        min_dmg = 561
        max_dmg = 715
        casting_time = 3

        yield from self._fire_spell(name='fireball', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time)

    def _fire_spell(self, name, min_dmg, max_dmg, casting_time, crit_modifier=0):
        casting_time = max(casting_time * self.casting_time_modifier, 1.5)
        if self._t2proc:
            casting_time = 1.5
            self._t2proc = False
            self.print("T2 proc")

        hit_chance = min(83 + self.hit, 99)
        hit = random.randint(1, 100) <= hit_chance

        crit_chance = self.crit + crit_modifier + self.combustion.crit_bonus
        crit = random.randint(1, 100) <= crit_chance

        dmg = random.randint(min_dmg, max_dmg)
        coeff = min(casting_time / 3.5, 1) if not name == 'fireball' else 1
        dmg += (self.sp + self.sp_bonus) * coeff

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
            if self.combustion.active:
                self.combustion.crit_bonus += 10
        elif not crit:
            self.print(f"{name} {dmg}")
            if self.combustion.active:
                self.combustion.crit_bonus += 10

        else:

            dmg = int(dmg * 1.5)
            self.print(f"{name} **{dmg}**")
            self.env.ignite.refresh(self, dmg)

            if self.combustion.active:
                self.combustion.charges -= 1
                if self.combustion.charges == 0:
                    self.combustion.crit_bonus = 0
                    self.print("Combustion ended")

        if name == 'scorch' and self.imp_scorch:
            self.env.debuffs.scorch()

        self.env.meter.register(self, dmg)
        if self.fullt2 and name == 'fireball':
            if random.randint(1, 100) <= 10:
                self._t2proc = True

    def _frost_spell(self, name, min_dmg, max_dmg, casting_time):
        casting_time = max(casting_time * self.casting_time_modifier, 1.5)
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
        dmg += (self.sp + self.sp_bonus) * coeff

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


class FireMage(Mage):
    def __init__(self,
                 name,
                 sp,
                 crit,
                 hit,
                 dmf=False,
                 **kwargs
                 ):
        super().__init__(
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
            **kwargs
        )


class ApFrostMage(Mage):
    def __init__(self,
                 name,
                 sp,
                 crit,
                 hit,
                 dmf=False,
                 **kwargs
                 ):
        super().__init__(
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


class WcMage(Mage):
    def __init__(self,
                 name,
                 sp,
                 crit,
                 hit,
                 dmf=False,
                 **kwargs
                 ):
        super().__init__(
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


class Cooldown:
    DURATION = NotImplemented

    def __init__(self, mage):
        self.mage = mage
        self.active = False
        self.used = False

    @property
    def usable(self):
        return not self.active and not self.used

    def activate(self):
        raise NotImplementedError


class AP(Cooldown):
    DURATION = 15
    DMG_MOD = 1.3

    @property
    def usable(self):
        return not self.active and not self.used and not self.mage.pi.active

    def activate(self):
        self.mage.dmg_modifier = self.DMG_MOD
        self.active = True
        self.mage.print(self.__class__.__name__)

        def callback(self):
            yield self.mage.env.timeout(self.DURATION)
            self.mage.dmg_modifier = 1
            self.active = False
            self.used = True

        self.mage.env.process(callback(self))


class Combustion(Cooldown):

    def __init__(self, mage):
        self.mage = mage
        self.charges = 0
        self.crit_bonus = 0
        self.used = False

    @property
    def active(self):
        return self.charges > 0

    def activate(self):
        self.mage.print("Combustion")
        self.charges = 3
        self.crit_bonus = 10
        self.used = True


class MQG(Cooldown):
    DURATION = 20

    @property
    def usable(self):
        return not self.active and not self.used and not self.mage.toep.active

    def activate(self):
        self.mage.casting_time_modifier = 0.75
        self.active = True
        self.mage.print("MQG")
        self.used = True

        def callback(self):
            yield self.mage.env.timeout(self.DURATION)
            self.mage.casting_time_modifier = 1
            self.active = False

        self.mage.env.process(callback(self))


class PI(AP):
    DURATION = 15
    DMG_MOD = 1.2

    @property
    def usable(self):
        return not self.active and not self.used and not self.mage.ap.active


class TOEP(Cooldown):
    DURATION = 15
    DMG_BONUS = 175

    @property
    def usable(self):
        return not self.active and not self.used and not self.mage.mqg.active

    def activate(self):
        self.mage.sp_bonus = 175
        self.active = True
        self.mage.print(self.__class__.__name__)
        self.used = True

        def callback(self):
            yield self.mage.env.timeout(self.DURATION)
            self.mage.sp_bonus = 0
            self.active = False

        self.mage.env.process(callback(self))
