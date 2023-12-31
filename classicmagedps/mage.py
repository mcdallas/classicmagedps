import random
from functools import partial

from classicmagedps.cooldown import *


class Mage:
    ROTATIONS = [
        'spam_fireballs',
        'spam_scorch',
        'spam_frostbolts',
        'smart_scorch',
        'smart_scorch_and_fireblast',
        'one_scorch_then_fireballs',
        'one_scorch_one_pyro_then_fb',
        'one_scorch_one_frostbolt_then_fb'
    ]

    def __init__(self,
                 name,
                 sp,
                 crit,
                 hit,
                 haste=0,
                 fire_blast_cooldown=8,
                 env=None,
                 firepower=True,
                 dmf=False,
                 imp_scorch=True,
                 incineration=False,
                 winters_chill=False,
                 arcane_instability=False,
                 piercing_ice=True,
                 fullt2=False,
                 pyro_on_instant_cast=False,
                 use_random_initial_delay=False,
                 lag=0.1
                 ):
        self.env = env
        self.name = name
        self.sp = sp
        self.crit = crit
        self.hit = hit
        self.haste = haste
        self.temp_haste = 0
        self.firepower = firepower
        self.dmf = dmf
        self.imp_scorch = imp_scorch
        self.incineration = incineration
        self.fire_blast_cooldown = fire_blast_cooldown
        self.pyro_on_instant_cast = pyro_on_instant_cast
        self.instant_cast = False
        self.dmg_modifier = 1
        self.winters_chill = winters_chill
        self.arcane_instability = arcane_instability
        self.piercing_ice = piercing_ice
        self.fullt2 = fullt2
        self.sp_bonus = 0
        self.fire_blast_remaining_cd = 0
        self.lag = lag
        self.use_random_initial_delay = use_random_initial_delay
        self.spell_travel_time = 0.5

        # cooldowns
        self.presence_of_mind = PresenceOfMind(self)
        self.combustion = Combustion(self)
        self.arcane_power = ArcanePower(self)
        self.power_infusion = PowerInfusion(self)
        self.toep = TOEP(self)
        self.mqg = MQG(self)

        if self.env:
            self.env.mages.append(self)

    def _random_delay(self, secs=2):
        if secs and self.use_random_initial_delay:
            delay = round(random.random() * secs, 2)
            yield self.env.timeout(delay)

    def _get_cast_time_modifier(self):
        if not self.haste and not self.temp_haste:
            return 1
        return 1 + (self.haste + self.temp_haste) / 100

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

    def _one_scorch_then_fireballs(self, delay=2, pyro_on_t2_proc=True, **cds):
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
            if self.env.debuffs.scorch_stacks < 5 or self.env.ignite.stacks == 5:
                yield from self.scorch()
            else:
                # check if scorch about to fall off
                if self.env.debuffs.scorch_timer <= 4.5:
                    yield from self.scorch()
                else:
                    yield from self.fireball()

    def _smart_scorch_and_fireblast(self, delay=2, **cds):
        """Cast scorch if less than 5 imp scorch stacks or if 5 stack ignite (to keep it rolling) else cast fireball"""
        yield from self._random_delay(delay)
        while True:
            self._use_cds(**cds)
            if self.env.ignite.stacks == 5 and self.fire_blast_remaining_cd <= 0:
                yield from self.fire_blast()
                self.fire_blast_remaining_cd = self.fire_blast_cooldown - 1.5
                # fire blast cd - gcd
            elif self.env.debuffs.scorch_stacks < 5 or self.env.ignite.stacks == 5:
                yield from self.scorch()
                self.fire_blast_remaining_cd -= 1.5
            else:
                # check if scorch about to fall off
                if self.env.debuffs.scorch_timer <= 5:
                    yield from self.scorch()
                    self.fire_blast_remaining_cd -= 1.5
                else:
                    yield from self.fireball()
                    self.fire_blast_remaining_cd -= 3

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

    def fireball(self, casting_time=3):
        min_dmg = 561
        max_dmg = 715

        yield from self._fire_spell(name='fireball', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time)

    def _fire_spell(self, name, min_dmg, max_dmg, casting_time, crit_modifier=0, cooldown=0.0):
        # unless this is t2 proc, calculate cast time
        if casting_time != 0:
            casting_time = max(casting_time / self._get_cast_time_modifier(), 1.5)

        hit_chance = min(83 + self.hit, 99)
        hit = random.randint(1, 100) <= hit_chance

        crit_chance = self.crit + crit_modifier + self.combustion.crit_bonus
        crit = random.randint(1, 100) <= crit_chance

        dmg = random.randint(min_dmg, max_dmg)
        coeff = min(casting_time / 3.5, 1) if not (name == 'fireball' or name == 'pyroblast') else 1
        dmg += (self.sp + self.sp_bonus) * coeff

        if self.firepower:
            dmg *= 1.1  # Fire Power
        if self.arcane_instability:
            dmg *= 1.03
        if self.env.debuffs.coe:
            dmg *= 1.1  # CoE
        if self.dmf:
            dmg *= 1.1

        dmg *= 1 + self.env.debuffs.scorch_stacks * 0.03  # imp. scorch

        dmg = int(dmg * self.dmg_modifier)
        if casting_time:
            yield self.env.timeout(casting_time + self.lag)

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

            if hasattr(self.env, 'ignite'):
                self.env.ignite.refresh(self, dmg)

            if self.combustion.active:
                self.combustion.charges -= 1
                if self.combustion.charges == 0:
                    self.combustion.crit_bonus = 0
                    self.print("Combustion ended")

        if name == 'fireball':
            self.env.debuffs.fireball_dot(self)

        if name == 'pyroblast':
            self.env.debuffs.pyroblast_dot(self, self.sp)

        if name == 'scorch' and self.imp_scorch and hit:
            self.env.debuffs.scorch()

        self.env.total_spell_dmg += dmg
        self.env.meter.register(self, dmg)

        # check if we can use instant cast
        if self.instant_cast:
            self.instant_cast = False
            yield self.env.timeout(0.05)  # small delay between spells
            if self.pyro_on_instant_cast:
                yield from self.pyroblast(casting_time=0)
            else:
                yield from self.fireball(casting_time=0)
            cooldown = 1.5
            self.print("Instant cast used")

        # check if we gained t2 proc
        if self.fullt2 and name == 'fireball':
            if random.randint(1, 100) <= 10:
                self.instant_cast = True
                self.print("T2 proc")

        # handle gcd
        if cooldown:
            # add some additional lag
            yield self.env.timeout(cooldown + self.lag)

    def _frost_spell(self, name, min_dmg, max_dmg, casting_time, cooldown=0.0):
        # unless this is t2 proc, calculate cast time
        if casting_time != 0:
            casting_time = max(casting_time / self._get_cast_time_modifier(), 1.5)

        hit_chance = min(83 + self.hit, 99)
        hit = random.randint(1, 100) <= hit_chance

        crit_chance = self.crit + self.env.debuffs.winters_chill_stacks * 2
        crit = random.randint(1, 100) <= crit_chance

        dmg = random.randint(min_dmg, max_dmg)
        coeff = min(casting_time / 3.5, 1) if not name == 'frostbolt' else 3 / 3.5 * 0.95
        dmg += (self.sp + self.sp_bonus) * coeff

        if self.piercing_ice:
            dmg *= 1.06  # Piercing Ice
        if self.arcane_instability:
            dmg *= 1.03
        if self.env.debuffs.coe:
            dmg *= 1.1  # CoE
        if self.dmf:
            dmg *= 1.1

        dmg = int(dmg * self.dmg_modifier)
        yield self.env.timeout(casting_time + self.lag)

        if not hit:
            dmg = 0
            self.print(f"{name} RESIST")
        elif not crit:
            self.print(f"{name} {dmg} {casting_time} {self.instant_cast}")
        else:
            dmg = int(dmg * 2)
            self.print(f"{name} **{dmg}**  {casting_time} {self.instant_cast}")

        if self.winters_chill:
            self.env.debuffs.winters_chill()

        self.env.meter.register(self, dmg)

        # check if we can use t2 proc
        if self.instant_cast:
            self.instant_cast = False
            yield self.env.timeout(0.05)  # small delay between spells
            if self.pyro_on_instant_cast:
                yield from self.pyroblast(casting_time=0)
            else:
                yield from self.frostbolt(casting_time=0)
            cooldown = 1.5
            self.print("Instant cast used")

        # check if we gained t2 proc
        if self.fullt2 and name == 'frostbolt':
            if random.randint(1, 100) <= 10:
                self.instant_cast = True
                self.print("T2 proc")

        # handle gcd
        if cooldown:
            # add some additional lag to cooldown
            yield self.env.timeout(cooldown + self.lag)

    def scorch(self):
        min_dmg = 237
        max_dmg = 280
        casting_time = 1.5
        crit_modifier = 4 if self.incineration else 0

        yield from self._fire_spell(name='scorch', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time,
                                    crit_modifier=crit_modifier)

    def fire_blast(self):
        min_dmg = 431
        max_dmg = 510
        casting_time = 0
        crit_modifier = 4 if self.incineration else 0

        yield from self._fire_spell(name='fireblast', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time,
                                    crit_modifier=crit_modifier, cooldown=1.5)

    def pyroblast(self, casting_time=6):
        min_dmg = 716
        max_dmg = 890

        yield from self._fire_spell(name='pyroblast', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time)

    def frostbolt(self, casting_time=2.5):
        min_dmg = 440
        max_dmg = 475

        yield from self._frost_spell(name='frostbolt', min_dmg=min_dmg, max_dmg=max_dmg, casting_time=casting_time)
