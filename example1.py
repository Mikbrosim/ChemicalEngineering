import mass_mole_balance as _
_.USE_MOLES = True
_.USE_MASS = True

Butanol = _.Substance(name="1-butanol")
Butanol.molar_mass=74.11

Ethanol = _.Substance(name="ethanol")
Ethanol.molar_mass=46.07

# Setup stream
s0_1 = _.Stream(idx=(0,1),fractions=[Ethanol,Butanol])
s0_1[Ethanol].mole_fraction=0.4
s0_1.moles=4000

s1_0_0 = _.Stream(idx=(1,0,0),fractions=[Ethanol,Butanol])
s1_0_0[Ethanol].mole_fraction=0.98

s1_0_1 = _.Stream(idx=(1,0,1),fractions=[Ethanol,Butanol])
s1_0_1[Butanol].mole_fraction=0.98

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

print(sol)
print(sol[s1_0_1[Butanol].mass])