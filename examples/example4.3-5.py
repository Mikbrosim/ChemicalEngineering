import mass_mole_balance as _
_.USE_MOLES = True
_.USE_MASS = True

# /1000 to keep equation in kg
benzene = B = _.Substance(name="B",molar_mass=78.11/1000)
toluene = T = _.Substance(name="T",molar_mass=92.13/1000)

s1 = _.Stream(idx=1,fractions=[B,T])
s1[B].mass_fraction=0.45
s1[T].mass_fraction=0.55
s1.mass = 2000*0.872

s2 = _.Stream(idx=2,fractions=[B,T])
s2[B].mole_fraction=0.95

s3 = _.Stream(idx=3,fractions=[B,T])
s3[B].mass=0.08*s1[B].mass

_.process(name=1,in_streams=[s1],out_streams=[s2,s3])

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
    s3[B].mass_fraction,
    s3[T].mass_fraction,
])