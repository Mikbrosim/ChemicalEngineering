from sympy import symbols as variable
from typing import Literal
import sympy
import time
import os

DOT_PATH = "./Graphviz/bin"

try:
    import pydot
    delimiter = ":" if os.name == "posix" else ";"
    if os.path.abspath(DOT_PATH) not in os.environ.get("PATH", "").split(delimiter):
        os.environ["PATH"] = os.environ.get("PATH", "") + delimiter + os.path.abspath(DOT_PATH)
except ImportError:
    pydot = None

USE_MOLES = False
USE_MASS = False
USE_VOLUME = False

def flag_check(mass=None,moles=None,volume=None,molar_mass=None,density=None,mass_fraction=None,mole_fraction=None,volume_fraction=None,mass_concentration=None):
    if mass!=None and not USE_MASS:raise KeyError("USE_MASS must be True, to be able to set mass")
    if moles!=None and not USE_MOLES:raise KeyError("USE_MOLES must be True, to be able to set moles")
    if volume!=None and not USE_VOLUME:raise KeyError("USE_VOLUME must be True, to be able to set volume")
    if density!=None and not (USE_VOLUME and USE_MASS):raise KeyError("USE_MASS and USE_VOLUME must be True, to be able to set density")
    if molar_mass!=None and not (USE_MOLES and USE_MASS):raise KeyError("USE_MASS and USE_MOLES must be True, to be able to set molar_mass")
    if mass_fraction!=None and not USE_MASS:raise KeyError("USE_MASS must be True, to be able to set mass_fraction")
    if mole_fraction!=None and not USE_MOLES:raise KeyError("USE_MOLES must be True, to be able to set mole_fraction")
    if volume_fraction!=None and not USE_VOLUME:raise KeyError("USE_VOLUME must be True, to be able to set volume_fraction")
    if mass_concentration!=None and not (USE_VOLUME and USE_MASS):raise KeyError("USE_MASS and USE_VOLUME must be True, to be able to set mass_concentration")


consts:dict[str,dict[sympy.Symbol,float|None]] = {}
relations:dict[str,list[sympy.Eq]] = {}
processes:dict[str,tuple[list["Stream"],list["Stream"]]] = {}
extra_eqs:list[sympy.Eq]=[]


class CombinedSubstanceFraction():
    """
    Acts as a combination of multiple substance fractions
    """
    def __init__(self,moles=None,mass=None,volume=None):
        self.moles = moles
        self.mass = mass
        self.volume = volume


class CombinedStream():
    """
    Acts as a combination of multiple streams
    """
    def __init__(self, fractions:dict["Substance","SubstanceFraction|CombinedSubstanceFraction"]={}):
        self.fractions = fractions

    def __zipped_streams(self, other,key):
        substances = set(list(self.fractions.keys())+list(other.fractions.keys()))
        for substance in substances:
            self_val:int = getattr(self.fractions.get(substance),key,0)
            other_val:int = getattr(other.fractions.get(substance),key,0)
            yield substance,self_val,other_val

    def __add__(self, other:"Stream|CombinedStream"):
        if not isinstance(other, (Stream,CombinedStream)):raise TypeError("Other must also be a Stream")
        fracs:dict["Substance","SubstanceFraction|CombinedSubstanceFraction"]={}

        if USE_MOLES:
            zipped_vals = self.__zipped_streams(other,"moles")
            for substance,self_val,other_val in zipped_vals:
                fracs[substance] = CombinedSubstanceFraction(moles=self_val + other_val)
        elif USE_MASS:
            zipped_vals = self.__zipped_streams(other,"mass")
            for substance,self_val,other_val in zipped_vals:
                fracs[substance] = CombinedSubstanceFraction(mass=self_val + other_val)
        elif USE_VOLUME:
            zipped_vals = self.__zipped_streams(other,"volume")
            for substance,self_val,other_val in zipped_vals:
                fracs[substance] = CombinedSubstanceFraction(mass=self_val + other_val)
        else:
            raise KeyError("Either USE_MOLES, USE_MASS or USE_VOLUME must be True")

        return CombinedStream(fractions=fracs)

    def __eq__(self, other:"Stream|CombinedStream"):
        if not isinstance(other, (Stream,CombinedStream)):raise TypeError("Other must also be a Stream")

        if USE_MOLES:
            zipped_vals = self.__zipped_streams(other,"moles")
        elif USE_MASS:
            zipped_vals = self.__zipped_streams(other,"mass")
        elif USE_VOLUME:
            zipped_vals = self.__zipped_streams(other,"volume")
        else:
            raise KeyError("Either USE_MOLES, USE_MASS or USE_VOLUME must be True")

        return [sympy.Eq(self_val,other_val) for substance,self_val,other_val in zipped_vals]


class Stream(CombinedStream):
    """
    Each stream has
    - `idx`, the idx of this stream used to make name
    - `fractions`, the fraction which this stream consists of

    - `mass`, the total amount of mass in the stream
    - `moles`, the total amount of moles in the stream
    - `volume`, the total amount of volume in the stream
    - `molar_mass`, the molar_mass of the stream
    - `density`. the density of the stream

    - `name`, the name of the stream, which is a suffix for sympy

    The mass must be equal to the sum of its fractions 
    The moles must be equal to the sum of its fractions 
    The molar_mass must be equal to the weighted average of its fractions 
    """
    def __init__(self, idx:int|tuple[int,...], fractions:list["Substance"], mass:float|None=None, moles:float|None=None, volume:float|None=None, molar_mass:float|None=None):
        if type(idx)==int:idx=(idx,)
        if type(idx)!=tuple:raise TypeError("idx must be either int or tuple")
        self.idx = idx
        self.name = f"S{'.'.join(map(str,self.idx))}"
        self.fractions = {substance:SubstanceFraction(substance=substance,stream=self) for substance in fractions}

        flag_check(mass=mass,moles=moles,molar_mass=molar_mass)
        consts[self.name]={}
        self.mass = mass
        self.moles = moles
        self.volume = volume
        self.molar_mass = molar_mass

        if self.name in relations:raise NameError(f"The idx, {idx}, provided to stream is not unique")
        relations[self.name]=[]
        if USE_MASS:relations[self.name].append(
            sympy.Eq(self.mass,sum(map(lambda fraction: fraction.mass,self.fractions.values())))
        )
        #if USE_MASS:relations[self.name].append(
        #    sympy.Eq(1,sum(map(lambda fraction: fraction.mass_fraction,self.fractions.values())))
        #)
        if USE_MOLES:relations[self.name].append(
            sympy.Eq(self.moles,sum(map(lambda fraction: fraction.moles,self.fractions.values())))
        )
        #if USE_MOLES:relations[self.name].append(
        #    sympy.Eq(1,sum(map(lambda fraction: fraction.mole_fraction,self.fractions.values())))
        #)
        if USE_VOLUME:relations[self.name].append(
            sympy.Eq(self.volume,sum(map(lambda fraction: fraction.volume,self.fractions.values())))
        )
        #if USE_VOLUME:relations[self.name].append(
        #    sympy.Eq(1,sum(map(lambda fraction: fraction.volume_fraction,self.fractions.values())))
        #)
        if USE_MOLES and USE_MASS:relations[self.name].append(
            sympy.Eq(self.molar_mass,sum(map(lambda fraction: fraction.substance.molar_mass*fraction.mole_fraction,self.fractions.values())))
        )
        

    @property
    def moles(self):return sympy.symbols(f'n_{{{self.name}}}')
    @moles.setter
    def moles(self,value:float|None):
        flag_check(moles=value)
        consts[self.name][self.moles] = value
    
    @property    
    def mass(self):return sympy.symbols(f'm_{{{self.name}}}')
    @mass.setter
    def mass(self,value:float|None):
        flag_check(mass=value)
        consts[self.name][self.mass] = value

    @property    
    def volume(self):return sympy.symbols(f'V_{{{self.name}}}')
    @volume.setter
    def volume(self,value:float|None):
        flag_check(volume=value)
        consts[self.name][self.volume] = value

    @property
    def molar_mass(self):return sympy.symbols(f'M_{{{self.name}}}')
    @molar_mass.setter
    def molar_mass(self,value:float|None):
        flag_check(molar_mass=value)
        consts[self.name][self.molar_mass] = value

    def __getitem__(self, substance:"Substance"):
        if not isinstance(substance, Substance):raise TypeError("Index must be a substance")
        if not substance in self.fractions:raise IndexError("Substance does not exist in stream")
        return self.fractions[substance]

    def __hash__(self):
        return int.from_bytes(self.name.encode())


class Substance():
    """
    Each substance has
    - `name`, the name of the substance, which is a suffix for sympy

    - `mass`, the total amount of mass in the substance
    - `moles`, the total amount of moles in the substance
    - `volume`, the total amount of volume in the substance
    - `molar_mass`, the molar_mass of the substance
    - `density`, the density of the substance

    - `fractions`, the fraction which this substance consists of
    """
    def __init__(self, name:str, mass:float|None=None, moles:float|None=None, volume:float|None=None, molar_mass:float|None=None, density:float|None=None):
        self.name = name

        flag_check(mass=mass,moles=moles,molar_mass=molar_mass)
        consts[self.name]={}
        self.mass = mass
        self.moles = moles
        self.volume = volume
        self.molar_mass = molar_mass
        self.density = density

        self.fractions = []

    @property
    def molar_mass(self):return sympy.symbols(f'M_{{{self.name}}}')
    @molar_mass.setter
    def molar_mass(self,value:float|None):
        flag_check(molar_mass=value)
        consts[self.name][self.molar_mass] = value

    @property
    def density(self):return sympy.symbols(f'p_{{{self.name}}}')
    @density.setter
    def density(self,value:float|None):
        flag_check(density=value)
        consts[self.name][self.density] = value

    @property    
    def moles(self):return sympy.symbols(f'n_{{{self.name}}}')
    @moles.setter
    def moles(self,value:float|None):
        flag_check(moles=value)
        consts[self.name][self.moles] = value
    
    @property    
    def mass(self):return sympy.symbols(f'm_{{{self.name}}}')
    @mass.setter
    def mass(self,value:float|None):
        flag_check(mass=value)
        consts[self.name][self.mass] = value
    
    @property    
    def volume(self):return sympy.symbols(f'm_{{{self.name}}}')
    @volume.setter
    def volume(self,value:float|None):
        flag_check(volume=value)
        consts[self.name][self.volume] = value

    def add_fraction(self,fraction):
        self.fractions.append(fraction)


class SubstanceFraction():
    """
    Each fraction of a substance has
    - `substance`, the substance which this is a fraction of
    - `stream`, the stream which this is a fraction of

    - `mass`, the mass of this fraction
    - `moles`, the amount of moles of this fraction
    - `volume`, the total amount of volume in the substance
    - `name`, the name of the fraction, which is a suffix for sympy
    """
    def __init__(self, substance:Substance, stream:Stream, mass:float|None=None, moles:float|None=None, volume:float|None=None, mole_fraction:float|None=None, mass_fraction:float|None=None, volume_fraction:float|None=None,mass_concentration:float|None=None):
        self.substance = substance
        self.stream = stream

        self.idx = self.stream.idx
        self.name = f"{stream.name}.{substance.name}"

        flag_check(mass=mass,moles=moles,volume=volume,mole_fraction=mole_fraction,mass_fraction=mass_fraction,volume_fraction=volume_fraction,mass_concentration=mass_concentration)
        consts[self.name]={}
        self.moles=moles
        self.mass=mass
        self.volume=volume
        self.mole_fraction=mole_fraction
        self.mass_fraction=mass_fraction
        self.volume_fraction=volume_fraction
        self.mass_concentration=mass_concentration

        self.substance.add_fraction(self)

        relations[self.name]=[]
        if USE_MASS:relations[self.name].append(
            sympy.Eq(self.mass,self.stream.mass*self.mass_fraction)
        )
        if USE_MOLES:relations[self.name].append(
            sympy.Eq(self.moles,self.stream.moles*self.mole_fraction)
        )
        if USE_VOLUME:relations[self.name].append(
            sympy.Eq(self.volume,self.stream.volume*self.volume_fraction)
        )
        if USE_MOLES and USE_MASS:relations[self.name].append(
            sympy.Eq(self.mass,self.moles*self.substance.molar_mass)
        )
        if USE_VOLUME and USE_MASS:relations[self.name].append(
            sympy.Eq(self.mass,self.volume*self.substance.density)
        )
        if USE_VOLUME and USE_MASS:relations[self.name].append(
            sympy.Eq(self.mass,self.stream.volume*self.mass_concentration)
        )

    @property
    def moles(self):return sympy.symbols(f'n_{{{self.name}}}')
    @moles.setter
    def moles(self,value:float|None):
        flag_check(moles=value)
        consts[self.name][self.moles] = value

    @property
    def mass(self):return sympy.symbols(f'm_{{{self.name}}}')
    @mass.setter
    def mass(self,value:float|None):
        flag_check(mass=value)
        consts[self.name][self.mass] = value

    @property
    def volume(self):return sympy.symbols(f'V_{{{self.name}}}')
    @volume.setter
    def volume(self,value:float|None):
        flag_check(volume=value)
        consts[self.name][self.volume] = value

    @property
    def mole_fraction(self):return sympy.symbols(f'n%_{{{self.name}}}')
    @mole_fraction.setter
    def mole_fraction(self,value:float|None):
        flag_check(mole_fraction=value)
        consts[self.name][self.mole_fraction] = value

    @property
    def mass_fraction(self):return sympy.symbols(f'm%_{{{self.name}}}')
    @mass_fraction.setter
    def mass_fraction(self,value:float|None):
        flag_check(mass_fraction=value)
        consts[self.name][self.mass_fraction] = value

    @property
    def volume_fraction(self):return sympy.symbols(f'V%_{{{self.name}}}')
    @volume_fraction.setter
    def volume_fraction(self,value:float|None):
        flag_check(volume_fraction=value)
        consts[self.name][self.volume_fraction] = value

    @property
    def mass_concentration(self):return sympy.symbols(f'Cm_{{{self.name}}}')
    @mass_concentration.setter
    def mass_concentration(self,value:float|None):
        flag_check(mass_concentration=value)
        consts[self.name][self.mass_concentration] = value


class CombinedReaction():
    def __init__(self, reactants=CombinedStream(), products=CombinedStream()):
        self.reactants = reactants
        self.products = products

    def __add__(self, other:"Reaction|CombinedReaction"):
        if not isinstance(other, (Reaction,CombinedReaction)):raise TypeError("Other must also be a Reaction")
        return CombinedReaction(reactants=self.reactants+other.reactants, products=self.products+other.products)


class Reaction(CombinedReaction):
    def __init__(self, name:str|int, reactants:dict[Substance,int|float], products:dict[Substance,int|float]):
        if type(name)==int:name=f"R{name}"
        if type(name)!=str:raise TypeError("Reaction must be supplied a name or an idx")
        self.name = name
        if len(reactants)==0 or len(products)==0:raise ValueError("The amount of reactants and products must be non-zero")
        if len(set(reactants)&set(products))!=0:raise ValueError("reactants must not be in products")

        if not USE_MOLES:
            raise KeyError("USE_MOLES must be True")

        self.reactants = CombinedStream({
            substance:CombinedSubstanceFraction(moles=sympy.symbols(f"n_{{{self.name}.{substance.name}}}"))
        for substance in reactants})

        self.products = CombinedStream({
            substance:CombinedSubstanceFraction(moles=sympy.symbols(f"n_{{{self.name}.{substance.name}}}"))
        for substance in products})

        relations[self.name]=[]
        for substance,v in reactants.items():
            relations[self.name].append(
                sympy.Eq(self.extent*v, self.reactants.fractions[substance].moles)
            )

        for substance,v in products.items():
            relations[self.name].append(
                sympy.Eq(self.extent*v, self.products.fractions[substance].moles)
            )

    @property
    def extent(self):return sympy.symbols(f'E_{{{self.name}}}')
    @extent.setter
    def extent(self,value:float|None):
        flag_check(moles=value)
        consts[self.name][self.extent] = value


class Process():
    """
    Constructs the relations of a process unit
    `name`, used for the relation
    `in_streams`, the streams going into the process
    `out_streams`,the streams going out of the process
    """
    def __init__(self, name:str|int, in_streams:list[Stream], out_streams:list[Stream], reactions:list[Reaction]=[]):
        # Make sure the function recieves the correct inputs
        if type(name)==int:name=f"P{name}"
        if type(name)!=str:raise TypeError("Process must be supplied a name or an idx")
        self.name = name
        if len(in_streams)==0 or len(out_streams)==0:raise ValueError("The amount of in_streams and out_streams must be non-zero")
        if len(set(in_streams)&set(out_streams))!=0:raise ValueError("in_streams must not be in out_streams")

        # Setup the equations which relate each of streams going in and out of the process
        _reactions = sum(reactions,start=CombinedReaction())

        _in = sum(in_streams,start=CombinedStream({}))
        _generated = _reactions.products
        _out = sum(out_streams,start=CombinedStream({}))
        _consumed = _reactions.reactants

        if self.name in relations:raise NameError(f"The name, {self.name}, provided to process is not unique")
        rel = _in + _generated == _out + _consumed
        if rel==None:raise NotImplementedError("This is not supposed to happen?")
        print(list(map(lambda x: x.name,_generated.fractions)))
        relations[self.name]=rel

        # Used to construct graph, which can be drawed
        processes[self.name]=(in_streams,out_streams)


def const_print():
    """
    Print all of the constants, in a nice way
    """
    print(" CONSTS ".center(20,"="))
    for stream_name,stream_consts in consts.items():
        for key,val in stream_consts.items():
            if val!=None:
                print(f"{key.name.ljust(20-1)}: {val}")
    print("".center(20,"="))


def relations_print():
    """
    Print the relations within each stream, in a nice way
    """
    print(" RELATIONS ".center(20,"="))
    for key,rels in relations.items():
        if rels!=None and len(rels)>0:
            eq = rels[0]
            print(f"{key.ljust(20-1)}: {eq.lhs} = {eq.rhs}")
            for eq in rels[1:]:
                print(" "*20,eq.lhs,"=",eq.rhs)
            print()
    print("".center(20,"="))


def combine_eqs():
    """
    Returns the eqs, as a combination of consts and relations
    """
    eqs:list[sympy.Eq] = []

    eqs+=extra_eqs

    for _eqs in relations.values():
        eqs+=_eqs

    for stream_name,stream_consts in consts.items():
        for key,val in stream_consts.items():
            if val!=None:
                eqs.append(sympy.Eq(key,val))

    return eqs


def reduce_equations(eqs:list[sympy.Eq],target_vars:list[sympy.Symbol]):
    eqs_len = len(eqs)
    for i in range(len(eqs)):
        reduced = False

        # Count the number of occurrences of each symbol in the eqs 
        occs:dict[sympy.Symbol,int] = dict()
        for eq in eqs:
            for sym in eq.free_symbols:
                if isinstance(sym,sympy.Symbol):
                    occs[sym]=occs.get(sym,0)+1

        # Mark the symbols only occurring once, as not needed, if they are not apart of the variables we are looking ofr
        not_needed:set[sympy.Symbol] = set()
        for sym,val in occs.items():
            if val == 1 and sym not in target_vars:
                not_needed.add(sym)

        # Remove the equations, which contains symbols which are neither the target nor an intermediate
        for eq in eqs:
            if len(eq.free_symbols & not_needed)>0:
                eqs.remove(eq)
                reduced=True
        if not reduced:break

    print(f"Removed {eqs_len-len(eqs)} unnecessary equations")
    return eqs


def solve_system(eqs:list[sympy.Eq],target_vars:None|list[sympy.Symbol]=None) -> list[dict[sympy.Symbol,float]]: 
    """
    Returns the solutions to the system
    """
    t=time.time()
    print(" SOLVING ".center(20,"="))
    if target_vars!=None:
        eqs = reduce_equations(eqs=eqs,target_vars=target_vars)
    print(f"Solving system of {len(eqs)} equations with {len(set(sum((list(eq.free_symbols) for eq in eqs),start=list())))} unknowns")
    sols = sympy.solve(eqs,domain=sympy.Reals,manual=True)
    print(f"Found {len(sols)} solutions in {round(1000*(time.time()-t))}ms")
    print("".center(20,"="))
    return sols


def solution_print(solution:dict[sympy.Symbol,float],variables:list[sympy.Symbol]):
    """
    Print the target variables, in a nice way
    """
    for var in variables:
        if var in solution:
            print(var,"=",solution[var])
        else:
            print(var,"=",None)
    for var,val in solution.items():
        if isinstance(val,(sympy.core.numbers.Float,sympy.core.numbers.Integer)) and val<0:print(f"Warning: {var}={val}<0")


def stream_label(stream:Stream):
    if type(stream)!=Stream:raise TypeError("Can only generate stream labels for streams...")
    
    stream_consts = []
    for var,val in consts[stream.name].items():
        if val!=None:
            stream_consts.append(f"{var} = {val}")

    fraction_consts = []
    for fraction in stream.fractions.values():
        for var,val in consts[fraction.name].items():
            if val!=None:
                fraction_consts.append(f"{var} = {val}")

    label = "\n".join(stream_consts+fraction_consts+[stream.name])
    return label


def drawer(out_file_name:str):
    if pydot==None:raise ImportError("the package pydot must be installed, in order to use this feature")

    # Preprocess
    in_streams:dict[Stream,str] = {}
    out_streams:dict[Stream,str] = {}
    p_names = processes.keys()
    for p_name,streams in processes.items():
        for stream in streams[0]:
            in_streams[stream]=p_name
        for stream in streams[1]:
            out_streams[stream]=p_name

    # Make the graph :D
    graph = pydot.Dot(graph_type='graph', rankdir='LR', splines='true')
    
    # Setup nodes
    node_counter = 0
    nodes:dict[str,str] = {}
    for p_name in p_names:
        node = pydot.Node(f"node_{node_counter}",label=p_name, shape="rectangle")
        nodes[p_name] = node.get_name()
        graph.add_node(node)
        node_counter+=1

    # Connect the nodes connected via streams
    connected_streams = set(in_streams.keys())&set(out_streams.keys())
    for stream in connected_streams:
        graph.add_edge(pydot.Edge(nodes[out_streams[stream]], nodes[in_streams[stream]], label=stream_label(stream), dir="forward"))
    
    # Connect the leftover nodes to the enviroment?
    leftover_streams = set(in_streams.keys())^set(out_streams.keys())
    for stream in leftover_streams:
        node_counter+=1
        dummy = pydot.Node(f"node_{node_counter}", shape="point", style="invisible")
        graph.add_node(dummy)
        if stream in in_streams.keys():
            graph.add_edge(pydot.Edge(dummy.get_name(), nodes[in_streams[stream]], label=stream_label(stream), dir="forward"))
        else:
            graph.add_edge(pydot.Edge(nodes[out_streams[stream]], dummy.get_name(), label=stream_label(stream), dir="forward"))

    # Save it to png!
    graph.write(path=out_file_name,prog='dot',format='png')