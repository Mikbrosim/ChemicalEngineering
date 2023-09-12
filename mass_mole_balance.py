import sympy
import time

try:
    import pydot
except ImportError:
    pydot = None

USE_MOLES = False
USE_MASS = False

def flag_check(mass=None,moles=None,molar_mass=None,mass_fraction=None,mole_fraction=None):
    if mass!=None and not USE_MASS:raise KeyError("USE_MASS must be True, to be able to set mass")
    if moles!=None and not USE_MOLES:raise KeyError("USE_MOLES must be True, to be able to set moles")
    if molar_mass!=None and not (USE_MOLES and USE_MASS):raise KeyError("USE_MASS and USE_MOLES must be True, to be able to set molar_mass")
    if mass_fraction!=None and not USE_MASS:raise KeyError("USE_MASS must be True, to be able to set mass_fraction")
    if mole_fraction!=None and not USE_MOLES:raise KeyError("USE_MOLES must be True, to be able to set mole_fraction")


consts:dict[str,dict[sympy.Symbol,float|None]] = {}
relations:dict[str,list[sympy.Eq]] = {}
processes:dict[str,tuple[list["Stream"],list["Stream"]]] = {}
#extra_eqs:list[sympy.Eq]=[]

class CombinedSubstanceFraction():
    """
    Acts as a combination of multiple substance fractions
    """
    def __init__(self,moles=None,mass=None):
        self.moles = moles
        self.mass = mass

class CombinedStream():
    """
    Acts as a combination of multiple streams
    """
    def __init__(self,fractions):
        self.fractions = fractions

    def __zipped_streams(self,other,key):
        substances = set(list(self.fractions.keys())+list(other.fractions.keys()))
        for substance in substances:
            self_val:int = getattr(self.fractions.get(substance),key,0)
            other_val:int = getattr(other.fractions.get(substance),key,0)
            yield substance,self_val,other_val

    def __add__(self,other:"Stream|CombinedStream"):
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
        else:
            raise KeyError("Either USE_MOLES or USE_MASS must be True")

        return CombinedStream(fractions=fracs)

    def __sub__(self,other:"Stream|CombinedStream"):
        raise NotImplementedError()
        if not isinstance(other, (Stream,CombinedStream)):raise TypeError("Other must also be a Stream")

        if USE_MOLES:
            zipped_vals = self.__zipped_streams(other,"moles")
            for substance,self_val,other_val in zipped_vals:
                fracs[substance] = CombinedSubstanceFraction(moles=self_val - other_val)
        elif USE_MASS:
            zipped_vals = self.__zipped_streams(other,"mass")
            for substance,self_val,other_val in zipped_vals:
                fracs[substance] = CombinedSubstanceFraction(mass=self_val - other_val)
        else:
            raise KeyError("Either USE_MOLES or USE_MASS must be True")

        return CombinedStream(fractions=fracs)

    def __eq__(self,other:"Stream|CombinedStream"):
        if not isinstance(other, (Stream,CombinedStream)):raise TypeError("Other must also be a Stream")

        if USE_MOLES:
            zipped_vals = self.__zipped_streams(other,"moles")
        elif USE_MASS:
            zipped_vals = self.__zipped_streams(other,"mass")
        else:
            raise KeyError("Either USE_MOLES or USE_MASS must be True")

        return [sympy.Eq(self_val,other_val) for substance,self_val,other_val in zipped_vals]


class Stream(CombinedStream):
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
    def __init__(self, idx:int|tuple[int,...], fractions:list["Substance"], mass:float|None=None, moles:float|None=None, molar_mass:float|None=None):
        if type(idx)==int:idx=(idx,)
        if type(idx)!=tuple:raise TypeError("idx must be either int or tuple")
        self.idx = idx
        self.name = f"S{'.'.join(map(str,self.idx))}"
        self.fractions = {substance:SubstanceFraction(substance=substance,stream=self) for substance in fractions}

        flag_check(mass=mass,moles=moles,molar_mass=molar_mass)
        consts[self.name]={}
        self.mass = mass
        self.moles = moles
        self.molar_mass = molar_mass

        if self.name in relations:raise NameError(f"The idx, {idx}, provided to stream is not unique")
        relations[self.name]=[]
        if USE_MASS:relations[self.name].append(
            sympy.Eq(self.mass,sum(map(lambda fraction: fraction.mass,self.fractions.values())))
        )
        if USE_MOLES:relations[self.name].append(
            sympy.Eq(self.moles,sum(map(lambda fraction: fraction.moles,self.fractions.values())))
        )
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
    - `molar_mass`, the molar_mass of the substance

    - `fractions`, the fraction which this substance consists of
    
    The mass must be equal to the sum of its fractions
    The moles must be equal to the sum of its fractions
    The molar_mass must be equal to the weighted average of its fractions 
    """
    def __init__(self, name, mass:float|None=None, moles:float|None=None, molar_mass:float|None=None):
        self.name = name

        flag_check(mass=mass,moles=moles,molar_mass=molar_mass)
        consts[self.name]={}
        self.mass = mass
        self.moles = moles
        self.molar_mass = molar_mass

        self.fractions = []

    @property
    def molar_mass(self):return sympy.symbols(f'M_{{{self.name}}}')
    @molar_mass.setter
    def molar_mass(self,value:float|None):
        flag_check(molar_mass=value)
        consts[self.name][self.molar_mass] = value
    
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

    def add_fraction(self,fraction):
        self.fractions.append(fraction)


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
        self.name = f"{stream.name}.{substance.name}"

        flag_check(mass=mass,moles=moles,mole_fraction=mole_fraction,mass_fraction=mass_fraction)
        consts[self.name]={}
        self.moles=moles
        self.mass=mass
        self.mole_fraction=mole_fraction
        self.mass_fraction=mass_fraction

        self.substance.add_fraction(self)

        relations[self.name]=[]
        if USE_MASS:relations[self.name].append(
            sympy.Eq(self.mass,self.stream.mass*self.mass_fraction)
        )
        if USE_MOLES:relations[self.name].append(
            sympy.Eq(self.moles,self.stream.moles*self.mole_fraction)
        )
        if USE_MOLES and USE_MASS:relations[self.name].append(
            sympy.Eq(self.mass,self.moles*self.substance.molar_mass)
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


def process(name:str|int,in_streams:list[Stream],out_streams:list[Stream]):
    """
    Constructs the relations of a process unit
    `name`, used for the relation
    `in_streams`, the streams going into the process
    `out_streams`,the streams going out of the process
    """
    # Make sure the function recieves the correct inputs
    if type(name)==int:name=f"P{name}"
    if type(name)!=str:raise TypeError("Process must be supplied a name or an idx")
    if len(in_streams)==0 or len(out_streams)==0:raise ValueError("The amount of in_streams and out_streams must be non-zero")

    # Setup the equations which relate each of streams going in and out of the process
    # sum(in) = sum(out)
    if name in relations:raise NameError(f"The name, {name}, provided to process is not unique")
    rel = sum(in_streams,start=CombinedStream({}))==sum(out_streams,start=CombinedStream({}))
    if rel==None:raise NotImplementedError("This is not supposed to happen?")
    relations[name]=rel

    # Used to construct graph, which can be drawed
    processes[name]=(in_streams,out_streams)

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

    #eqs+=extra_eqs

    for _eqs in relations.values():
        eqs+=_eqs

    for stream_name,stream_consts in consts.items():
        for key,val in stream_consts.items():
            if val!=None:
                eqs.append(sympy.Eq(key,val))

    return eqs


def solve_system(eqs) -> list[dict[sympy.Symbol,float]]: 
    """
    Returns the solutions to the system
    """
    t=time.time()
    print(" SOLVING ".center(20,"="))
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