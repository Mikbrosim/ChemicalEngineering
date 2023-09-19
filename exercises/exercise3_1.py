import material_balance as _

_.USE_MASS=True
_.USE_VOLUME=True

# Substance
solvent = _.Substance("solvent")
water = H2O = _.Substance("H2O")
novobiocin = _.Substance("novobiocin")

# Streams
s1 = _.Stream(idx=1,fractions=[water,novobiocin])
s1.volume = 3
s1[novobiocin].mass_concentration = 23

s2 = _.Stream(idx=2,fractions=[solvent])
s2.volume = 0.25

s3 = _.Stream(idx=3,fractions=[water,novobiocin])
s3.volume = s1.volume # I guess this actually should be the volume of the water, not the total volume, but this makes it solveable, by assuming the novobiocin has no volume :shrug:

s4 = _.Stream(idx=4,fractions=[solvent,novobiocin])
s4.volume = s2.volume
s4[novobiocin].mass = 16

# Process
_.Process(name=1,in_streams=[s1,s2],out_streams=[s3,s4])

K_novobiocin = _.variable('K_novobiocin')
_.extra_eqs.append(_.sympy.Eq(K_novobiocin,s4[novobiocin].mass_concentration/s3[novobiocin].mass_concentration))

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))
eqs = _.combine_eqs()

# Solve
target_vars = [
    s3[novobiocin].mass,
    s4[novobiocin].mass,
    s3[novobiocin].mass_concentration,
    s4[novobiocin].mass_concentration,
    K_novobiocin,
]
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
m_{S3.novobiocin} = 53.0000000000000
m_{S4.novobiocin} = 16.0000000000000
Cm_{S3.novobiocin} = 17.6666666666667
Cm_{S4.novobiocin} = 64.0000000000000
K_novobiocin = 3.62264150943396
""".rstrip())