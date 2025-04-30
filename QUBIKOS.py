import networkx as nx
import random
from qiskit import QuantumCircuit,qasm2

def random_node_index(number_of_nodes):
  # Generate random initial mapping

  node_index_list=[i for i in range(number_of_nodes)]
  random.shuffle(node_index_list)

  return node_index_list

def check_valid_move(G,start_node,candidate_node):
  # Check whether a physical edges is valid for SWAP

  start_neighbor=set(G.neighbors(start_node))
  candidate_neioghbor=set(G.neighbors(candidate_node))
  difference=(start_neighbor|candidate_neioghbor)-{start_node,candidate_node}-(start_neighbor & candidate_neioghbor)
  return len(difference)>0

def find_valid_swap_graph(coupling_list):
  # Output a list of physical edges valid for SWAP

  G = nx.Graph()
  G.add_edges_from(coupling_list)
  sub_coupling_list=[]
  for start,end in coupling_list:
    if check_valid_move(G,start,end):
      sub_coupling_list.append((start,end))

  G_sub=nx.Graph()
  G_sub.add_edges_from(sub_coupling_list)
  return G_sub

def random_walk(G, start_node, length):
  walk = []
  current_node = start_node
  previous_node=None

  for _ in range(length):
      neighbors = list(G.neighbors(current_node))
      if len(neighbors)>1 and not previous_node is None :
        neighbors.remove(previous_node)
      next_node = random.choice(neighbors)
      walk.append((current_node,next_node))
      previous_node=current_node
      current_node=next_node

  return walk

def physical_to_program(coupling_list,node_index_list):
  #Get program qubit index given a physical coupling list and a mapping

  new_coupling_list=[]
  for i,j in coupling_list:
    new_coupling_list.append((node_index_list[i],node_index_list[j]))

  return new_coupling_list


def find_edge(bfs_list,target):
  for i in range(len(bfs_list)):
    if target==bfs_list[i][1]:
      return i
  return -1


def non_isomorphic_graph(mapping,swap_operation,coupling):
  G=nx.Graph()
  G.add_edges_from(coupling)
  start_neighbor=set(G.neighbors(swap_operation[0]))
  candidate_neioghbor=set(G.neighbors(swap_operation[1]))
  difference=(start_neighbor|candidate_neioghbor)-{swap_operation[0],swap_operation[1]}-(start_neighbor & candidate_neioghbor)
  p=random.choice(list(difference))
  special_gate=None
  if p in list(G.neighbors(swap_operation[0])):
    special_gate=[(p,swap_operation[1])]
  else:
    special_gate=[(p,swap_operation[0])]

  p=random.choice(list(special_gate[0]))
  occupied_qubit=[]
  s=[]
  for p0,p1 in G.edges:
    if p0==p or p1==p:
      s.append((p0,p1))
      occupied_qubit.append(p0)
    elif G.degree[p0]>G.degree[p]:
      s.append((p0,p1))
      occupied_qubit.append(p0)
    elif G.degree[p1]>G.degree[p]:
      s.append((p0,p1))
      occupied_qubit.append(p1)
  occupied_qubit=list(set(occupied_qubit))
  occupied_qubit=[mapping[p] for p in occupied_qubit]
  special_gate=physical_to_program(special_gate,mapping)
  s=physical_to_program(s,mapping)

  return s,special_gate,occupied_qubit

def generate_dependence_gates(coupling, mapping,starting_node,required_nodes):
#  print("necessary node:",required_nodes)
#  print("start node",starting_node)
  program_coupling=physical_to_program(coupling,mapping)
#  print("program coupling",program_coupling)
  G=nx.Graph()
  G.add_edges_from(program_coupling)
  necessary_nodes=[starting_node]+required_nodes
  nodes=list(G.nodes)
  for node in nodes:
    if not node in necessary_nodes:
      G_copy=G.copy()
      G_copy.remove_node(node)
      if nx.is_connected(G_copy):
        if random.random()<0.5:
          G.remove_node(node)

  visited_edges=list(nx.bfs_edges(G,starting_node))
#  print("orginal",visited_edges)
  keep=[False for _ in range(len(visited_edges))]

  for node in required_nodes:
#    print("start with",node)
    target=node
    while target!=starting_node:
      i=find_edge(visited_edges,target)
      keep[i]=True
      target=visited_edges[i][0]
#      print("Trace back",visited_edges[i])
#    print("Initial target",target)
#    print("Initial trace back",visited_edges[i])


  dependency=[]
  for i in range(len(visited_edges)):
    if keep[i]:
      dependency.append(visited_edges[i])


  return dependency

def build_section(swap_operation,coupling,mapping,initial_gate=None):
  s,special_gate,occupied_qubit=non_isomorphic_graph(mapping,swap_operation,coupling)
  start=random.choice(list(special_gate[0]))
  subsequent_dependecy=generate_dependence_gates(coupling,mapping,start,occupied_qubit)
  subsequent_dependecy.reverse()
  prior_dependecy=[]
  if not initial_gate is None:
    start=random.choice(list(initial_gate[0]))
#    print(occupied_qubit)
    prior_dependecy=generate_dependence_gates(coupling,mapping,start,occupied_qubit)
#    print("Prior choice:",p)

  return prior_dependecy,s,subsequent_dependecy,special_gate

def select_single_qubit_gate(qc,qubit, choice=None):
  if choice==None:
    choice=random.randint(0,5)
  if choice==0:
    qc.x(qubit)
  elif choice==1:
    qc.y(qubit)
  elif choice==2:
    qc.z(qubit)
  elif choice==3:
    qc.h(qubit)
  elif choice==4:
    qc.s(qubit)
  else:
    qc.t(qubit)
  
  return choice

def select_two_qubit_gate(qc,control,target,choice=None):
  if choice==None:
    choice=random.randint(0,1)
  if choice==0:
    qc.cx(control,target)
  else:
    qc.cz(control,target)
  
  return choice

def checker(coupling_list,initial_mapping,answer):
  if len(initial_mapping)!=len(set(initial_mapping)):
    return False

  current_mapping=initial_mapping.copy()
#  print(current_mapping)
  for gate in answer:
    if len(gate)==2:
      p0=current_mapping.index(gate[0])
      p1=current_mapping.index(gate[1])
      if not ((p0,p1) in coupling_list or (p1,p0) in coupling_list):
        return False

    else:
      p0=current_mapping.index(gate[1])
      p1=current_mapping.index(gate[2])
      if not ((p0,p1) in coupling_list or (p1,p0) in coupling_list):
        return False
      current_mapping[p0]=gate[2]
      current_mapping[p1]=gate[1]
 #     print(current_mapping)

  return True

def generate_qubikos_circuit(benchmark_file_name,compiled_file_name,physical_coupling_list,number_of_swap,number_of_two_qubit_gates,number_of_single_qubit_gate=0):
  number_of_nodes=max([max(i) for i in physical_coupling_list])+1
  initial_mapping=random_node_index(number_of_nodes)
  current_mapping=initial_mapping.copy()
  list_of_mapping=[initial_mapping.copy()]
  program_coupling_list=physical_to_program(physical_coupling_list,initial_mapping)
  list_of_program_couplings=[program_coupling_list]
#  print(initial_mapping)
#  print(coupling_list)
  benchmark_circuit,compiled_circuit=QuantumCircuit(number_of_nodes),QuantumCircuit(number_of_nodes)
  initial_gate=None
  least_number_of_gates=0
  list_of_prior_dependence,list_of_target_edges,list_of_later_dependence,list_of_special_gate,list_of_swap_gate=[],[],[],[],[]
  G_swap=find_valid_swap_graph(physical_coupling_list)

  while number_of_swap>0:
    path_length=random.randint(1, number_of_swap)
    path_start=random.randint(0, number_of_nodes-1)
    random_path=random_walk(G_swap,path_start,path_length)
    number_of_swap-=len(random_path)

    for physical_swap in random_path:
      swap=(current_mapping[physical_swap[0]],current_mapping[physical_swap[1]])
      list_of_swap_gate.append((physical_swap[0],physical_swap[1]))
      initial_dependence,target_edges,later_dependence,special_gate=build_section(physical_swap,physical_coupling_list,current_mapping,initial_gate)
      least_number_of_gates+=len(initial_dependence)+len(target_edges)+len(later_dependence)+1
      list_of_prior_dependence.append(initial_dependence)
      list_of_target_edges.append(target_edges)
      list_of_later_dependence.append(later_dependence)
      list_of_special_gate.append(special_gate)
      initial_gate=special_gate

      current_mapping[physical_swap[0]]=swap[1]
      current_mapping[physical_swap[1]]=swap[0]
      list_of_mapping.append(current_mapping.copy())
      coupling_list=physical_to_program(physical_coupling_list,current_mapping)
      list_of_program_couplings.append(coupling_list)

  block_list=[]
  number_of_swap=len(list_of_swap_gate)
  for i in range(number_of_swap):
    block=list_of_prior_dependence[i]+list_of_target_edges[i]+list_of_later_dependence[i]
    block_list.append(block)
  block_list.append([])
#  print(block_list)
  list_of_special_gate.append([])
  list_of_swap_gate.append([])
#  print("list_of_prior_dependency",list_of_prior_dependence)
#  print("list_of_isomorphic_gate:",list_of_target_edges)
#  print("list_of_later_dependency",list_of_later_dependence)
#  print("list_of_special_gate:",list_of_special_gate)
#  print()

  if least_number_of_gates>number_of_two_qubit_gates:
#    print("Output backbone circuit")
#    print("Require at least",least_number_of_gates,"gates")
    number_of_two_qubit_gates=least_number_of_gates

#  print("Least number of gates",least_number_of_gates)
#  print("Total number of gates",number_of_gates)
  two_qubit_redundant=number_of_two_qubit_gates-least_number_of_gates
  remaining_single_qubit_gates=number_of_single_qubit_gate

  for i in range(number_of_swap+1):
    if i==number_of_swap:
      current_redundant=two_qubit_redundant
      current_single_qubit_gates_num=remaining_single_qubit_gates
    else:
      current_redundant=random.randint(0,two_qubit_redundant)
      current_single_qubit_gates_num=random.randint(0,int(remaining_single_qubit_gates/number_of_swap*2))
#      print("Before",redundant)
#      print("Number of redudant gates",current_redundant)
      two_qubit_redundant-=current_redundant
      remaining_single_qubit_gates-=current_single_qubit_gates_num
#      print("After",redundant)

#    print("Redundant gate left",redundant)
#    print("Before",len(block_list[i]))
    current_edge_choice=[element for element in list_of_program_couplings[i] if random.random()<0.5]
    redundant_gates=random.choices(current_edge_choice,k=current_redundant)
    for j in range(len(redundant_gates)):
      position=random.randint(0,len(redundant_gates))
      block_list[i].insert(position,redundant_gates[j])
#      print("After",len(block_list[i]))
 #   print("block",block[i])
 #   print("special",list_of_special_gate[i])
    
#    print("pro",list_of_program_couplings)
    single_qubit_gates=random.choices([i for i in range(number_of_nodes)],k=current_single_qubit_gates_num)
    for program_q in single_qubit_gates:
      choice=select_single_qubit_gate(benchmark_circuit,program_q)
      current_mapping=list_of_mapping[i]
      physical_q=current_mapping.index(program_q)
      select_single_qubit_gate(compiled_circuit,physical_q,choice)

    for control,target in block_list[i]:
      choice=select_two_qubit_gate(benchmark_circuit,control,target)
      current_mapping=list_of_mapping[i]
      physical_control,physical_target=current_mapping.index(control),current_mapping.index(target)
      select_two_qubit_gate(compiled_circuit,physical_control,physical_target,choice)
    
    if len(list_of_swap_gate[i])>0:
      physical_control,physical_target=list_of_swap_gate[i]
      compiled_circuit.swap(physical_control,physical_target)
    
    if len(list_of_special_gate[i])>0:
      control,target=list_of_special_gate[i][0]
      choice=select_two_qubit_gate(benchmark_circuit,control,target)
      current_mapping=list_of_mapping[i+1]
      physical_control,physical_target=current_mapping.index(control),current_mapping.index(target)
      select_two_qubit_gate(compiled_circuit,physical_control,physical_target,choice)

  
#  print(initial_mapping)
  qasm2.dump(benchmark_circuit,benchmark_file_name)
  qasm2.dump(compiled_circuit,compiled_file_name)

#  print("Final circuit",circuit)
  return benchmark_circuit,compiled_circuit

