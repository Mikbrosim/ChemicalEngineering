import mass_mole_balance as _
_.USE_MOLES = False
_.USE_MASS = True

# Setup compounds
B = _.Substance(name="B")

T = _.Substance(name="T")

# Setup stream
s1 = _.Stream(idx=(1,),fractions=[B,T])
s1[B].mass=500
s1[T].mass=500

s2 = _.Stream(idx=(2,),fractions=[B,T])
s2[B].mass=450

s3 = _.Stream(idx=(3,),fractions=[B,T])
s3[T].mass=475

# Setup processes
_.process(name=1,in_streams=[s1],out_streams=[s2,s3])

# Print eqs
_.const_print()
_.relations_print()

# Solve
eqs = _.combine_eqs()
sols = _.solve_system(eqs)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

#print(sol)
print(sol[s2[T].mass])
print(sol[s3[B].mass])