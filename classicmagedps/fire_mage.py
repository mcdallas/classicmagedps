from classicmagedps import Mage


class FireMage(Mage):
    def __init__(self,
                 name,
                 sp,
                 crit,
                 hit,
                 dmf=False,
                 fire_blast_cooldown=6.5,
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
            winters_chill=False,
            arcane_instability=False,
            piercing_ice=False,
            pyro_on_instant_cast=True,
            fire_blast_cooldown=fire_blast_cooldown,
            **kwargs
        )
