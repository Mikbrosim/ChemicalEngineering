import material_balance as _

_.USE_MASS=True
_.USE_MOLES=True
_.USE_VOLUME=True

# Substance
water = H2O = _.Substance("H2O",molar_mass=18.02)
glucose = C6H12O6 = _.Substance("C6H12O6",molar_mass=180.2)
oxygen = O2 = _.Substance("O2",molar_mass=32.00)
ammonia = NH3 = _.Substance("NH3",molar_mass=17.03)
carbon_dioxide = CO2 = _.Substance("CO2",molar_mass=44.01)
biomass = C8H13NO4 = _.Substance("biomass",molar_mass=44.01)
nitrogen = N2 = _.Substance("N2")

# Streams
s1 = _.Stream(1,[water,ammonia])
s1[ammonia].mass_fraction=0.008
s1.mass=80000

s2 = _.Stream(2,[CO2,O2,N2])
s2[CO2].volume_fraction = 0.10
s2[O2].volume_fraction = 0.11
s2[N2].volume_fraction = 0.79
s2.volume=100

s3 = _.Stream(3,[CO2,O2,N2])
s3.volume=100.2
s3[CO2].moles=0

s4 = _.Stream(4,[biomass,water,ammonia,glucose])
#s4[ammonia].moles=0

# Reactions
r1 = _.Reaction(1,reactants={CO2:10,H2O:8,NH3:0.72},products={biomass:0.5,C6H12O6:1,O2:10.2})

# Process
_.Process(name=1,in_streams=[s1,s2],out_streams=[s3,s4],reactions=[r1])

_.extra_eqs.append(_.sympy.Eq(
    10**5 * s3[N2].volume , s3[N2].moles * 8.314 * 298
    ))
_.extra_eqs.append(_.sympy.Eq(
    10**5 * s2[N2].volume , s2[N2].moles * 8.314 * 298
    ))
_.extra_eqs.append(_.sympy.Eq(
    10**5 * s3[O2].volume , s3[O2].moles * 8.314 * 298
    ))
_.extra_eqs.append(_.sympy.Eq(
    10**5 * s2[O2].volume , s2[O2].moles * 8.314 * 298
    ))
_.extra_eqs.append(_.sympy.Eq(
    10**5 * s3[CO2].volume , s3[CO2].moles * 8.314 * 298
    ))
_.extra_eqs.append(_.sympy.Eq(
    10**5 * s2[CO2].volume , s2[CO2].moles * 8.314 * 298
    ))

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))
eqs = _.combine_eqs()

# Solve
target_vars = [
    s4[biomass].mass,
    s3[N2].volume_fraction,
    s3[CO2].volume_fraction,
    s3[O2].volume_fraction,
]
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
m_{S4.biomass} = 888.167932152930
V%_{S3.N2} = 0.788423153692615
V%_{S3.CO2} = 0.0
V%_{S3.O2} = 0.211576846307385
""".rstrip())