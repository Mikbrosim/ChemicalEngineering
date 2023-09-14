import material_balance as _
_.USE_MOLES = False
_.USE_MASS = True

acetone = A = _.Substance(name="A")
water = W = _.Substance(name="W")
MIBK = M = _.Substance(name="M")

s1 = _.Stream(idx=1,fractions=[A,W])
s1.mass = 100
s1[A].mass_fraction=0.500
s1[W].mass_fraction=0.500

s2 = _.Stream(idx=2,fractions=[M])
s2.mass = 100

s3 = _.Stream(idx=3,fractions=[A,W,M])
s4 = _.Stream(idx=4,fractions=[A,W,M])
s4[A].mass_fraction=0.275

s5 = _.Stream(idx=5,fractions=[M])
s5.mass = 75

s6 = _.Stream(idx=6,fractions=[A,W,M])
s6[A].mass_fraction=0.090
s6[M].mass_fraction=0.880
s6[W].mass_fraction=0.030

s7 = _.Stream(idx=7,fractions=[A,W,M])
s7.mass=43.1
s7[W].mass_fraction = 0.931
s7[A].mass_fraction = 0.053
s7[M].mass_fraction = 0.016

s8 = _.Stream(idx=8,fractions=[A,W,M])
s8[A].mass_fraction=0.97
s8[M].mass_fraction=0.02
s8[W].mass_fraction=0.01

s9 = _.Stream(idx=9,fractions=[A,W,M])
s10 = _.Stream(idx=10,fractions=[A,W,M])

_.Process(name=1,in_streams=[s1,s2],out_streams=[s3,s4])
_.Process(name=2,in_streams=[s3,s5],out_streams=[s6,s7])
_.Process(name=3,in_streams=[s4,s6],out_streams=[s10])
_.Process(name=4,in_streams=[s10],out_streams=[s8,s9])


# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))

# Solve
target_vars = [
    s3.mass,
    s3[A].mass_fraction,
    s3[W].mass_fraction,
    s3[M].mass_fraction,
    s4.mass,
    s4[A].mass_fraction,
    s4[W].mass_fraction,
    s4[M].mass_fraction,
    s6.mass,
    s6[A].mass_fraction,
    s6[W].mass_fraction,
    s6[M].mass_fraction,
    s10.mass,
    s10[A].mass_fraction,
    s10[W].mass_fraction,
    s10[M].mass_fraction,
    s8.mass,
    s8[A].mass_fraction,
    s8[W].mass_fraction,
    s8[M].mass_fraction,
    s9.mass,
    s9[A].mass_fraction,
    s9[W].mass_fraction,
    s9[M].mass_fraction,
]
eqs = _.combine_eqs()
sols = _.solve_system(eqs,target_vars=target_vars)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,target_vars)

print("\nExpected return"+"""
m_{S3} = 54.8935135135135
m%_{S3.A} = 0.183914556930864
m%_{S3.W} = 0.778414473230727
m%_{S3.M} = 0.0376709698384095
m_{S4} = 145.106486486486
m%_{S4.A} = 0.275000000000000
m%_{S4.W} = 0.0501017891799871
m%_{S4.M} = 0.674898210820013
m_{S6} = 86.7935135135135
m%_{S6.A} = 0.0900000000000000
m%_{S6.W} = 0.0300000000000000
m%_{S6.M} = 0.880000000000000
m_{S10} = 231.900000000000
m%_{S10.A} = 0.205759810263044
m%_{S10.W} = 0.0425782664941785
m%_{S10.M} = 0.751661923242777
m_{S8} = 231.9 - m_{S9}
m%_{S8.A} = 0.970000000000000
m%_{S8.W} = 0.0100000000000000
m%_{S8.M} = 0.0200000000000000
m_{S9} = None
m%_{S9.A} = 0.0001*(9700.0*m_{S9} - 1772273.0)/m_{S9}
m%_{S9.W} = 0.0001*(100.0*m_{S9} + 75549.0)/m_{S9}
m%_{S9.M} = 0.0004*(50.0*m_{S9} + 424181.0)/m_{S9}
""".rstrip())