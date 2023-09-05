import main as _
_.USE_MOLES = False
_.USE_MASS = True

# Setup compounds
B = _.Substance(name="B")

T = _.Substance(name="T")

# Setup stream
s0_1 = _.Stream(idx=(0,1),fractions=[B,T])
s0_1[B].mass=500
s0_1[T].mass=500

s1_0_0 = _.Stream(idx=(1,0,0),fractions=[B,T])
s1_0_0[B].mass=450

s1_0_1 = _.Stream(idx=(1,0,1),fractions=[B,T])
s1_0_1[T].mass=475

# Unit 1
_.extra_eqs += s0_1 == (s1_0_0 + s1_0_1)

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
print(sol[s1_0_0[T].mass])
print(sol[s1_0_1[B].mass])