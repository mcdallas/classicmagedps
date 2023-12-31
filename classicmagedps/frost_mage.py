from classicmagedps import Mage


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
            winters_chill=False,
            arcane_instability=True,
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
            winters_chill=True,
            arcane_instability=False,
            piercing_ice=True,
            **kwargs
        )