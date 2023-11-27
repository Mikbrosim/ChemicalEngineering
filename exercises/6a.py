import material_balance as _

_.USE_MASS=True
_.USE_MOLES=True

# Const
pressure = 10**5
R = 8.314
T = 40 + 273.15

# Substance
C6H12O7 = _.Substance("C6H12O7",molar_mass=196.2)
biomass = _.Substance("biomass",molar_mass=21.43)
CH4N2O = _.Substance("CH4N2O",molar_mass=60.06)
CO2 = _.Substance("CO2")
H2O = _.Substance("H2O",molar_mass=18.02)
C6H12O6 = _.Substance("C6H12O6",molar_mass=180.2)
O2 = _.Substance("O2")
N2 = _.Substance("N2")

# Streams
s1 = _.Stream(1,[N2,O2])
s1[N2].mole_fraction=0.79
s1[O2].mole_fraction=0.21

s2 = _.Stream(2,[H2O,CH4N2O,C6H12O6])
s2.mass = 120*1000
s2[CH4N2O].mass_fraction=0.02
s2[C6H12O6].mass_fraction=0.25

s3 = _.Stream(3,[CO2,N2,O2])
#s3[CO2].mole_fraction = 0.107

s4 = _.Stream(4,[H2O,CH4N2O,C6H12O6,C6H12O7,biomass])

# Reactions
r1 = _.Reaction(1,reactants={C6H12O6:7,O2:9},products={C6H12O7:6,CO2:6,H2O:6})
r2 = _.Reaction(2,reactants={C6H12O6:1,O2:0.25,CH4N2O:0.5},products={biomass:5,CO2:1.5,H2O:2.5})

# Process
_.Process(name=1,in_streams=[s1,s2],out_streams=[s3,s4],reactions=[r1,r2])

# Eqs
_.extra_eqs.append(_.sympy.Eq(
    pressure * 40 , s1.moles * R * T
    ))
_.extra_eqs.append(_.sympy.Eq(
    pressure * 40 , s3.moles * R * T
    ))
_.extra_eqs.append(_.sympy.Eq(
    s2[C6H12O6].moles*0.03, s4[C6H12O6].moles
    ))

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))
eqs = _.combine_eqs()

# Solve
target_vars = [
    s3[CO2].mole_fraction,
    s4[C6H12O7].mass,
    s4[biomass].mass,
    s4[CH4N2O].moles,
]
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
n%_{S3.CO2} = 0.107345545342055
m_{S4.C6H12O7} = 20223.6994356153
m_{S4.biomass} = 4417.87848017569
n_{S4.CH4N2O} = 19.3446480786788
""".rstrip())