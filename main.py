import sympy
import time

consts:dict[sympy.Symbol,float|None] = {}
relations:dict[str,list[sympy.Eq]] = {}
extra_eqs:list[sympy.Eq]=[]

class CombinedSubstanceFraction():
    """
    Acts as a combination of multiple substance fractions
    """
    def __init__(self,moles):
        self.moles = moles
class CombinedStream():
    """
    Acts as a combination of multiple streams
    """
    def __init__(self,fractions):
        self.fractions = fractions

    def __sub__(self,other:"Stream|CombinedStream"):return other.__sub__(self)
    def __add__(self,other:"Stream|CombinedStream"):return other.__add__(self)
    def __eq__(self,other:"Stream|CombinedStream"):return other.__eq__(self)


class Stream():
    """
    Each stream has
    - `idx`, the idx of this stream used to make name
    - `fractions`, the fraction which this stream consists of

    - `mass`, the total amount of mass in the stream
    - `moles`, the total amount of moles in the stream
    - `molar_mass`, the molar_mass of the stream

    - `name`, the name of the stream, which is a suffix for sympy

    The mass must be equal to the sum of its fractions 
    The moles must be equal to the sum of its fractions 
    The molar_mass must be equal to the weighted average of its fractions 
    """
    def __init__(self, idx:tuple[int,int]|tuple[int,int,int], fractions:list["Substance"], mass:float|None=None, moles:float|None=None, molar_mass:float|None=None):
        self.idx = idx
        self.name = f"S.{'.'.join(map(str,self.idx))}"
        self.fractions = {substance:SubstanceFraction(substance=substance,stream=self) for substance in fractions}

        self.mass = mass
        self.moles = moles
        self.molar_mass = molar_mass

        relations[self.name]=[
            sympy.Eq(sum(map(lambda fraction: fraction.mass,self.fractions.values())),self.mass),
            sympy.Eq(sum(map(lambda fraction: fraction.moles,self.fractions.values())),self.moles),
            sympy.Eq(sum(map(lambda fraction: fraction.substance.molar_mass*fraction.mole_fraction,self.fractions.values())),self.molar_mass),
        ]
        

    @property
    def moles(self):return sympy.symbols(f'n_{self.name}')
    @moles.setter
    def moles(self,value:float|None):consts[self.moles] = value
    
    @property    
    def mass(self):return sympy.symbols(f'm_{self.name}')
    @mass.setter
    def mass(self,value:float|None):consts[self.mass] = value

    @property
    def molar_mass(self):return sympy.symbols(f'M_{self.name}')
    @molar_mass.setter
    def molar_mass(self,value:float|None):consts[self.molar_mass] = value

    def __getitem__(self, substance:"Substance"):
        if not isinstance(substance, Substance):raise TypeError("Index must be a substance")
        if not substance in self.fractions:raise IndexError("Substance does not exist in stream")
        return self.fractions[substance]

    def __add__(self,other:"Stream|CombinedStream"):
        if not isinstance(other, (Stream,CombinedStream)):raise TypeError("Other must also be a Stream")
        if not self.fractions.keys()==other.fractions.keys():raise TypeError("The two Streams must contain the same fractions")
        return CombinedStream(fractions={substance:CombinedSubstanceFraction(self.fractions[substance].moles + other.fractions[substance].moles) for substance in self.fractions.keys()})

    def __sub__(self,other:"Stream|CombinedStream"):
        raise NotImplementedError()

        if not isinstance(other, (Stream,CombinedStream)):raise TypeError("Other must also be a Stream")
        if not self.fractions.keys()==other.fractions.keys():raise TypeError("The two Streams must contain the same fractions")
        return CombinedStream(fractions={substance:CombinedSubstanceFraction(self.fractions[substance].moles - other.fractions[substance].moles) for substance in self.fractions.keys()})

    def __eq__(self,other:"Stream|CombinedStream"):
        if not isinstance(other, (Stream,CombinedStream)):raise TypeError("Other must also be a Stream")
        if not self.fractions.keys()==other.fractions.keys():raise TypeError("The two Streams must contain the same fractions")
        return [sympy.Eq(self.fractions[substance].moles,other.fractions[substance].moles) for substance in self.fractions.keys()]


class Substance():
    """
    Each substance has
    - `name`, the name of the substance, which is a suffix for sympy

    - `mass`, the total amount of mass in the substance
    - `moles`, the total amount of moles in the substance
    - `molar_mass`, the molar_mass of the substance

    - `fractions`, the fraction which this substance consists of
    
    The mass must be equal to the sum of its fractions
    The moles must be equal to the sum of its fractions
    The molar_mass must be equal to the weighted average of its fractions 
    """
    def __init__(self, name, mass:float|None=None, moles:float|None=None, molar_mass:float|None=None):
        self.name = name

        self.mass = mass
        self.moles = moles
        self.molar_mass = molar_mass

        self.fractions = []

    @property
    def molar_mass(self):return sympy.symbols(f'M_{self.name}')
    @molar_mass.setter
    def molar_mass(self,value:float|None):consts[self.molar_mass] = value
    
    @property    
    def moles(self):return sympy.symbols(f'n_{self.name}')
    @moles.setter
    def moles(self,value:float|None):consts[self.moles] = value
    
    @property    
    def mass(self):return sympy.symbols(f'm_{self.name}')
    @mass.setter
    def mass(self,value:float|None):consts[self.mass] = value

    def add_fraction(self,fraction):
        self.fractions.append(fraction)

    """
    def update_relations(self):
        relations[self.name]=[
            sum(map(lambda fraction: fraction.mass,self.fractions))==self.mass,
            sum(map(lambda fraction: fraction.moles,self.fractions))==self.moles,
            sum(map(lambda fraction: fraction.molar_mass,self.fractions))==self.mass,
        ]
    """

    """
    def __getitem__(self, index):
        if isinstance(index, tuple) and len(index) == 2:
            row, col = index
            print(index)
        else:
            raise TypeError("Index must be a tuple (in, out)")
    """

class SubstanceFraction():
    """
    Each fraction of a substance has
    - `substance`, the substance which this is a fraction of
    - `stream`, the stream which this is a fraction of

    - `mass`, the mass of this fraction
    - `moles`, the amount of moles of this fraction
    
    - `name`, the name of the fraction, which is a suffix for sympy
    """
    def __init__(self, substance:Substance, stream:Stream, mass:float|None=None, moles:float|None=None, mole_fraction:float|None=None, mass_fraction:float|None=None):
        self.substance = substance
        self.stream = stream

        self.idx = self.stream.idx
        #self.name = f"{'.'.join(map(str,self.idx))}.{substance.name}"
        self.name = f"{stream.name}.{substance.name}"

        self.moles=moles
        self.mass=mass
        self.mole_fraction=mole_fraction
        self.mass_fraction=mass_fraction

        self.substance.add_fraction(self)

        relations[self.name]=[
            sympy.Eq(self.moles*self.substance.molar_mass,self.mass),
            sympy.Eq(self.moles,self.stream.moles*self.mole_fraction),
            sympy.Eq(self.mass,self.stream.mass*self.mass_fraction),
        ]

    @property
    def moles(self):return sympy.symbols(f'n_{self.name}')
    @moles.setter
    def moles(self,value:float|None):consts[self.moles] = value

    @property
    def mass(self):return sympy.symbols(f'm_{self.name}')
    @mass.setter
    def mass(self,value:float|None):consts[self.mass] = value

    @property
    def mole_fraction(self):return sympy.symbols(f'n%_{self.name}')
    @mole_fraction.setter
    def mole_fraction(self,value:float|None):consts[self.mole_fraction] = value

    @property
    def mass_fraction(self):return sympy.symbols(f'm%_{self.name}')
    @mass_fraction.setter
    def mass_fraction(self,value:float|None):consts[self.mass_fraction] = value

def const_print():
    """
    Print all of the constants, in a nice way
    """
    print(" CONSTS ".center(20,"="))
    for key,val in consts.items():
        if val!=None:
            print(f"{key.name.ljust(20-1)}: {val}")
    print("".center(20,"="))

def relations_print():
    """
    Print the relations within each stream, in a nice way
    """
    print(" RELATIONS ".center(20,"="))
    for key,val in relations.items():
        if val!=None:
            print(f"{key.ljust(20-1)}: {val}")
    print("".center(20,"="))

def combine_eqs():
    """
    Returns the eqs, as a combination of consts and relations
    """
    eqs:list[sympy.Eq] = []

    eqs+=extra_eqs

    for _eqs in relations.values():
        eqs+=_eqs

    for key,val in consts.items():
        if val!=None:
            eqs.append(sympy.Eq(key,val))

    return eqs

def solve_system(eqs) -> list[dict[sympy.Symbol,float]]: 
    """
    Returns the solutions to the system
    """
    t=time.time()
    print(" SOLVING ".center(20,"="))
    sols = sympy.solve(eqs)
    print(f"Found {len(sols)} solutions in {round(1000*(time.time()-t))}ms")
    print("".center(20,"="))
    return sols

if __name__=="__main__":
    # Setup compounds
    Butanol = Substance(name="1-butanol")
    Butanol.molar_mass=74.11

    Ethanol = Substance(name="ethanol")
    Ethanol.molar_mass=46.07

    # Setup stream
    s0_1 = Stream(idx=(0,1),fractions=[Ethanol,Butanol])
    s0_1[Ethanol].mole_fraction=0.4
    s0_1.moles=4000

    s1_0_0 = Stream(idx=(1,0,0),fractions=[Ethanol,Butanol])
    s1_0_0[Ethanol].mole_fraction=0.98

    s1_0_1 = Stream(idx=(1,0,1),fractions=[Ethanol,Butanol])
    s1_0_1[Butanol].mole_fraction=0.98

    # Unit 1
    extra_eqs += s0_1 == (s1_0_0 + s1_0_1)

    # Print eqs
    const_print()
    relations_print()

    # Solve
    eqs = combine_eqs()
    sols = solve_system(eqs)
    assert len(sols)!=0,"No solutions found"
    assert len(sols)==1,"Multiple solutions found"
    sol = sols[0]

    print(sol)
    #for k,v in sol.items():
    #    print(f"{k}={v}")
    #print(sol[s0_1[Ethanol].mass])