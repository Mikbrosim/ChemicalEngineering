import material_balance as _

_.USE_MASS=True
_.USE_VOLUME=True
_.USE_MOLES=True

N2 = _.Substance(name="N2")
O2 = _.Substance(name="O2")
# 1 g/mL    18.02 g/mol
H2O = _.Substance(name="H2O",density=1,molar_mass=18.02)

s1 = _.Stream(idx=1,fractions=[H2O])
s1[H2O].volume=20 # 20 cm^3 = 20 mL

s2 = _.Stream(idx=2, fractions=[O2,N2])
s2[O2].mole_fraction=0.21

s3 = _.Stream(idx=3, fractions=[O2])
s3.moles=s2.moles/5

s4 = _.Stream(idx=4, fractions=[H2O,O2,N2])
s4[H2O].mole_fraction=0.015

_.Process(name="Humidifier",in_streams=[s1,s2,s3],out_streams=[s4])

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))

# Solve
target_vars = [
    s1.moles,
    s2.moles,
    s3.moles,
    s4.moles,
    s4[N2].mole_fraction,
    s4[O2].mole_fraction,
    s4[H2O].mole_fraction,
]
eqs = _.combine_eqs()
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
n_{S1} = 1.10987791342952
n_{S2} = 60.7349858182267
n_{S3} = 12.1469971636453
n_{S4} = 73.9918608953015
n%_{S4.N2} = 0.648458333333333
n%_{S4.O2} = 0.336541666666667
n%_{S4.H2O} = 0.0150000000000000
""".rstrip())