import mass_mole_balance as _
_.USE_MOLES = True
_.USE_MASS = True

Butanol = _.Substance(name="1-butanol")
Butanol.molar_mass=74.11

Ethanol = _.Substance(name="ethanol")
Ethanol.molar_mass=46.07

# Setup stream
s1 = _.Stream(idx=(1,),fractions=[Ethanol,Butanol])
s1[Ethanol].mole_fraction=0.4
s1.moles=4000

s2 = _.Stream(idx=(2,),fractions=[Ethanol,Butanol])
s2[Ethanol].mole_fraction=0.98

s3 = _.Stream(idx=(3,),fractions=[Ethanol,Butanol])
s3[Butanol].mole_fraction=0.98

# Process 1
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

print(f"{sol[s2[Ethanol].moles]=}")
print(f"{sol[s2[Butanol].moles]=}")
print(f"{sol[s3[Ethanol].moles]=}")
print(f"{sol[s3[Butanol].moles]=}")