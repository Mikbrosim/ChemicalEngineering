import material_balance as _

_.USE_MASS=True
_.USE_VOLUME=True

biomass = _.Substance(name="Bio")
water = H2O = _.Substance(name="H2O",density=1)

s1 = _.Stream(idx=1,fractions=[water,biomass])
s1[biomass].mass_concentration = 30
s1.volume = 1

s2 = _.Stream(idx=2,fractions=[water,biomass])

s3 = _.Stream(idx=3,fractions=[water,biomass])
s3.volume = 0.80 * s1.volume


_.Process(name="Membrane",in_streams=[s1],out_streams=[s2,s3])
_.extra_eqs.append(
    _.sympy.Eq(0.98,1-s3[biomass].mass_concentration/s1[biomass].mass_concentration)
    )

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))

# Solve
target_vars = [
    s2[biomass].mass_concentration,
    s3[biomass].mass_concentration,
]
eqs = _.combine_eqs()
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
Cm_{S2.Bio} = 147.600000000000
Cm_{S3.Bio} = 0.600000000000000
""".rstrip())