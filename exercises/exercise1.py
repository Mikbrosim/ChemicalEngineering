import material_balance as _
_.USE_MOLES = True
_.USE_MASS = False

Butanol = _.Substance(name="1-butanol")
#Butanol.molar_mass=74.11

Ethanol = _.Substance(name="ethanol")
#Ethanol.molar_mass=46.07

# Setup stream
s1 = _.Stream(idx=1,fractions=[Ethanol,Butanol])
s1[Ethanol].mole_fraction=0.4
s1.moles=4000

s2 = _.Stream(idx=2,fractions=[Ethanol,Butanol])
s2[Ethanol].mole_fraction=0.98

s3 = _.Stream(idx=3,fractions=[Ethanol,Butanol])
s3[Butanol].mole_fraction=0.98

# Process 1
_.Process(name=1,in_streams=[s1],out_streams=[s2,s3])

# Print eqs
_.const_print()
_.relations_print()

# Solve
target_vars = [
    s2[Ethanol].moles,
    s2[Butanol].moles,
    s3[Ethanol].moles,
    s3[Butanol].moles,
]
eqs = _.combine_eqs()
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
n_{S2.ethanol} = 1551.66666666667
n_{S2.1-butanol} = 31.6666666666667
n_{S3.ethanol} = 48.3333333333333
n_{S3.1-butanol} = 2368.33333333333
""".rstrip())