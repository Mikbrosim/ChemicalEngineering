import material_balance as _

_.USE_MASS=True
_.USE_VOLUME=True

NaOH = _.Substance(name="NaOH")
H2O = _.Substance(name="H2O",density=1)

s1 = _.Stream(idx=1,fractions=[H2O,NaOH])
s1.mass=1
s1[NaOH].mass_fraction=0.20

s2 = _.Stream(idx=2,fractions=[H2O])

s3 = _.Stream(idx=3,fractions=[H2O,NaOH])
s3[NaOH].mass_fraction=0.08


_.Process(name="Dilution",in_streams=[s1,s2],out_streams=[s3])

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))

# Solve
target_vars = [
    s2[H2O].volume,
    s3.mass,
]
eqs = _.combine_eqs()
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
V_{S2.H2O} = 1.50000000000000
m_{S3} = 2.50000000000000
""".rstrip())