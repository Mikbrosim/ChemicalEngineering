import mass_mole_balance as _
_.USE_MOLES = False
_.USE_MASS = True

water = H2O = _.Substance(name="H2O")
potassium_chromate = K2CrO4 = _.Substance(name="K2CrO4")

# Input
s0 = _.Stream(idx=0,fractions=[H2O,K2CrO4])
s0.mass=4500
s0[K2CrO4].mass_fraction=0.333

# Combined
s1 = _.Stream(idx=1,fractions=[H2O,K2CrO4])

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

_.process("Combiner",in_streams=[s0,s6],out_streams=[s1])
_.process("Evap",in_streams=[s1],out_streams=[s2,s3])
_.process("Crystalizer",in_streams=[s3],out_streams=[s4,s5,s6])

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
    s2.mass,
    s4.mass,
    s1.mass,
    s3.mass,
    s6.mass,
    s0.mass,
])