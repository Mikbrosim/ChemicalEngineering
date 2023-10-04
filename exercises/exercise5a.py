import material_balance as _

_.USE_MASS=True
_.USE_MOLES=True

# Substance
water = _.Substance("water",molar_mass=18.02)
acetic_acid = _.Substance("acetic_acid",molar_mass=60.05)
oxygen = _.Substance("oxygen")
ethanol = _.Substance("ethanol")
nitrogen = _.Substance("nitrogen")

# Streams
s1 = _.Stream(1,[oxygen,nitrogen])
s1[oxygen].mole_fraction = 0.21
s1.moles=200

s2 = _.Stream(2,[ethanol,water])

s3 = _.Stream(3,[oxygen,nitrogen])

s4 = _.Stream(4,[acetic_acid,water])
s4[acetic_acid].mass = 2000 # 2 kg
s4[acetic_acid].mass_fraction = 0.12

# Reactions
r1 = _.Reaction(1,reactants={ethanol:1,oxygen:1},products={acetic_acid:1,water:1})

# Process
_.Process(name=1,in_streams=[s1,s2],out_streams=[s3,s4],reactions=[r1])

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))
eqs = _.combine_eqs()

# Solve
target_vars = [
    s2.moles,
    s2[water].mole_fraction,
    s2[ethanol].mole_fraction,
    s3.moles,
    s3[oxygen].mole_fraction,
    s3[nitrogen].mole_fraction,
]
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
n_{S2} = 813.910469848317
n%_{S2.water} = 0.959079554916358
n%_{S2.ethanol} = 0.0409204450836424
n_{S3} = 166.694421315570
n%_{S3.oxygen} = 0.0521578421578422
n%_{S3.nitrogen} = 0.947842157842158
""".rstrip())