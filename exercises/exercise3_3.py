import material_balance as _

_.USE_MASS=True
_.USE_VOLUME=True

# Substance
solvent = _.Substance("solvent")
water = H2O = _.Substance("H2O")
novobiocin = _.Substance("novobiocin")

K_novobiocin = 3.62264150943396

# Streams
s1 = _.Stream(idx=1,fractions=[water,novobiocin])
s1.volume = 85
s1[novobiocin].mass_concentration = 23

s2 = _.Stream(idx=2,fractions=[solvent])

s3 = _.Stream(idx=3,fractions=[water,novobiocin])
s3.volume = s1.volume

s4 = _.Stream(idx=4,fractions=[solvent,novobiocin])
s4.volume = s2.volume

s5 = _.Stream(idx=5,fractions=[water,novobiocin])
s5.volume = s1.volume
s5[novobiocin].mass_concentration = 1

s6 = _.Stream(idx=6,fractions=[solvent,novobiocin])
s6.volume = s2.volume

# Process - counter current
_.Process(name=1,in_streams=[s1,s4],out_streams=[s3,s6])
_.Process(name=2,in_streams=[s3,s2],out_streams=[s5,s4])

_.extra_eqs += [
    _.sympy.Eq(K_novobiocin,s6[novobiocin].mass_concentration/s3[novobiocin].mass_concentration),
    _.sympy.Eq(K_novobiocin,s4[novobiocin].mass_concentration/s5[novobiocin].mass_concentration),
]

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))
eqs = _.combine_eqs()

# Solve
target_vars = [
    s2[solvent].volume,
]
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
#assert len(sols)==1,"Multiple solutions found"
sol = sols[1]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
V_{S2.solvent} = 98.9455338539454
""".rstrip())