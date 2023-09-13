import material_balance as _
_.USE_MOLES = False
_.USE_MASS = True

A = _.Substance(name="A")
B = _.Substance(name="B")

s1 = _.Stream(idx=1,fractions=[A,B])
s1.mass = 100
s1[A].mass_fraction=0.500
s1[B].mass_fraction=0.500

s2 = _.Stream(idx=2,fractions=[A,B])
s2.mass = 40
s2[A].mass_fraction=0.900
s2[B].mass_fraction=0.100

s3 = _.Stream(idx=3,fractions=[A,B])

s4 = _.Stream(idx=4,fractions=[A,B])
s4.mass = 30
s4[A].mass_fraction=0.300
s4[B].mass_fraction=0.700

s5 = _.Stream(idx=5,fractions=[A,B])

s6 = _.Stream(idx=6,fractions=[A,B])
s6.mass = 30
s6[A].mass_fraction=0.600
s6[B].mass_fraction=0.400

s7 = _.Stream(idx=7,fractions=[A,B])

_.Process(name=1,in_streams=[s1],out_streams=[s2,s3])
_.Process(name=2,in_streams=[s3,s4],out_streams=[s5])
_.Process(name=3,in_streams=[s5],out_streams=[s6,s7])

# Print eqs
_.const_print()
_.relations_print()
_.drawer(__file__.replace("py","png"))

# Solve
eqs = _.combine_eqs()
sols = _.solve_system(eqs)
assert len(sols)!=0,"No solutions found"
assert len(sols)==1,"Multiple solutions found"
sol = sols[0]

_.solution_print(sol,[
    s3.mass,
    s3[A].mass_fraction,
    s3[B].mass_fraction,
    s5.mass,
    s5[A].mass_fraction,
    s5[B].mass_fraction,
    s7.mass,
    s7[A].mass_fraction,
    s7[B].mass_fraction,
])

print("\nExpected return"+"""
m_{S3} = 60.0000000000000
m%_{S3.A} = 0.233333333333333
m%_{S3.B} = 0.766666666666667
m_{S5} = 90.0000000000000
m%_{S5.A} = 0.255555555555556
m%_{S5.B} = 0.744444444444444
m_{S7} = 60.0000000000000
m%_{S7.A} = 0.0833333333333333
m%_{S7.B} = 0.916666666666667
""".rstrip())