import mass_mole_balance as _
_.USE_MOLES = True
_.USE_MASS = False

water = H2O = _.Substance(name="H2O")
dry_air = DA = _.Substance(name="DA")

# Fresh air
s1 = _.Stream(idx=1,fractions=[H2O,DA])
s1[H2O].mole_fraction=0.0400

# Combined air
s2 = _.Stream(idx=2,fractions=[H2O,DA])
s2[H2O].mole_fraction=0.0230

# Condensate
s3 = _.Stream(idx=3,fractions=[H2O])

# Out air
s4 = _.Stream(idx=4,fractions=[H2O,DA])
s4[H2O].mole_fraction=0.0170

# Recycle air
s5 = _.Stream(idx=5,fractions=[H2O,DA])
s5[H2O].mole_fraction=s4[H2O].mole_fraction

# Dehumidified air
s6 = _.Stream(idx=6,fractions=[H2O,DA])
s6[H2O].mole_fraction=s4[H2O].mole_fraction
s6.moles=100

_.process("Combined",in_streams=[s1,s5],out_streams=[s2])
_.process("Air Cond",in_streams=[s2],out_streams=[s3,s4])
_.process("Recycler",in_streams=[s4],out_streams=[s5,s6])

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
    s1.moles,
    s3.moles,
    s5.moles,
])

print("\nExpected return"+"""
n_{S1} = 102.395833333333
n_{S3} = 2.39583333333333
n_{S5} = 290.121527777778
""".rstrip())