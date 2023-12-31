import material_balance as _
_.USE_MOLES = False
_.USE_MASS = True

# Setup compounds
methanol = ch3o3 = _.Substance(name="CH3OH")

water = h2o = _.Substance(name="H2O")

# Setup stream
s1 = _.Stream(idx=1,fractions=[ch3o3,h2o])
s1.mass=200
s1[ch3o3].mass_fraction=0.400

s2 = _.Stream(idx=2,fractions=[ch3o3,h2o])
s2.mass=150
s2[ch3o3].mass_fraction=0.700

s3 = _.Stream(idx=3,fractions=[ch3o3,h2o])

# Setup processes
_.Process(name=1,in_streams=[s1,s2],out_streams=[s3])

# Print eqs
_.const_print()
_.relations_print()

# Solve
target_vars = [
    s3.mass,
    s3[ch3o3].mass_fraction,
    s3[h2o].mass_fraction,
]
eqs = _.combine_eqs()
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
m_{S3} = 350.000000000000
m%_{S3.CH3OH} = 0.528571428571429
m%_{S3.H2O} = 0.471428571428571
""".rstrip())