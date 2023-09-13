import material_balance as _
_.USE_MOLES = False
_.USE_MASS = True

water = H2O = _.Substance(name="H2O")
potassium_chromate = K2CrO4 = _.Substance(name="K2CrO4")

# Input
s1 = _.Stream(idx=1,fractions=[H2O,K2CrO4])
s1.mass=4500
s1[K2CrO4].mass_fraction=0.333

# Condensate
s2 = _.Stream(idx=2,fractions=[H2O])
s2[H2O].mass_fraction=1

# Evap -> Crystal
s3 = _.Stream(idx=3,fractions=[H2O,K2CrO4])
s3[K2CrO4].mass_fraction=0.494

# Filtrate
s5 = _.Stream(idx=5,fractions=[H2O,K2CrO4])
s5[K2CrO4].mass_fraction=0.364

# Filter cake
s4 = _.Stream(idx=4,fractions=[K2CrO4])
s4[K2CrO4].mass=0.95*(s4.mass+s5.mass)

# Recycle
s6 = _.Stream(idx=6,fractions=[H2O,K2CrO4])
s6[K2CrO4].mass_fraction=0.364

_.Process("Evap",in_streams=[s1],out_streams=[s2,s3])
_.Process("Crystalizer",in_streams=[s3],out_streams=[s4,s5,s6])

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))

# Solve
eqs = _.combine_eqs()
sols = _.solve_system(eqs)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,[
    s4.mass,
    s6.mass,
])

print("\nExpected return"+"""
m_{S4} = 620.034756703078
m_{S6} = 2380.73264476599
""".rstrip())