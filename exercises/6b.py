import material_balance as _

_.USE_MASS=True
_.USE_MOLES=True

# Const
pressure = 10**5
R = 8.314
T = 35 + 273.15

# Substance
H2O = _.Substance("H2O",molar_mass=18.02)
C12H22O11 = _.Substance("C12H22O11",molar_mass=342.1)
C4H10O = _.Substance("C4H10O",molar_mass=74.11)
CO2 = _.Substance("CO2",molar_mass=44.01)
C5H10O3 = _.Substance("C5H10O3",molar_mass=118.3)
air = _.Substance("air")

# Streams
s1 = _.Stream(1,[C12H22O11,H2O])
s1.mass = 200*1000
s1[C12H22O11].mass_fraction=0.25

s2 = _.Stream(2,[air])

s3 = _.Stream(3,[C5H10O3,C4H10O,H2O])

s4 = _.Stream(4,[air,CO2])
s4[CO2].mole_fraction=0.300

# Reactions
r1 = _.Reaction(1,reactants={C12H22O11:1},products={C4H10O:2,CO2:4,H2O:1})
r2 = _.Reaction(2,reactants={C12H22O11:1},products={C5H10O3:2,CO2:2,H2O:1})

# Process
_.Process(name=1,in_streams=[s1,s2],out_streams=[s3,s4],reactions=[r1,r2])

# Eqs
_.extra_eqs.append(_.sympy.Eq(
    pressure * 45 , s4.moles * R * T
    ))

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))
eqs = _.combine_eqs()

# Solve
target_vars = [
    s3[C5H10O3].mass,
    s3[C4H10O].mass,
]
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
m_{S3.C5H10O3} = 6824.00328811664
m_{S3.C4H10O} = 17388.3038330029
""".rstrip())