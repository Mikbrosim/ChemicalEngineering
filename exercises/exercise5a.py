import material_balance as _

_.USE_MASS=True
_.USE_MOLES=True

# Substance
water = _.Substance("water",molar_mass=18.02)
ethanol = _.Substance("ethanol",molar_mass=60.05)
oxygen = _.Substance("oxygen",molar_mass=32.00)
acetic_acid = _.Substance("acetic_acid",molar_mass=46.07)
nitrogen = _.Substance("nitrogen",molar_mass=28.01)

# Streams
s1 = _.Stream(1,[oxygen,nitrogen])
s1[oxygen].mole_fraction = 0.21
s1.moles=200

s2 = _.Stream(2,[ethanol,water])

s3 = _.Stream(3,[acetic_acid,water])
#s3[acetic_acid].mass = 2000 # 2 kg
s3[acetic_acid].mass_fraction = 0.12

s4 = _.Stream(4,[oxygen,nitrogen])
s4[oxygen].moles=0

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
    s2[ethanol].moles,
    s3[water].moles,
    s3[acetic_acid].mass,
    s3[acetic_acid].mass_fraction,
    s1[oxygen].mole_fraction,
    s1[oxygen].moles,
    s4[oxygen].mole_fraction,
    s4[oxygen].moles,
    s4[nitrogen].moles,
    r1.reactants.fractions[oxygen].moles,
    r1.reactants.fractions[ethanol].moles,
    s4.moles,
]
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
n_{S2.ethanol} = 42.0000000000000
n_{S3.water} = 787.433962264151
m_{S3.acetic_acid} = 1934.94000000000
m%_{S3.acetic_acid} = 0.120000000000000
n%_{S1.oxygen} = 0.210000000000000
n_{S1.oxygen} = 42.0000000000000
n%_{S4.oxygen} = 0.0
n_{S4.oxygen} = 0.0
n_{S4.nitrogen} = 158.000000000000
n_{R1.oxygen} = 42.0000000000000
n_{R1.ethanol} = 42.0000000000000
n_{S4} = 158.000000000000
""".rstrip())