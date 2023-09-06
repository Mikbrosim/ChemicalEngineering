import mass_mole_balance as _
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
_.process(name=1,in_streams=[s1,s2],out_streams=[s3])

# Print eqs
_.const_print()
_.relations_print()

# Solve
eqs = _.combine_eqs()
sols = _.solve_system(eqs)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,[
    s3.mass,
    s3[ch3o3].mass_fraction,
    s3[h2o].mass_fraction,
])