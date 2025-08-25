import importlib.util
import os
from graph import *
from response import *
import networkx as nx
import matplotlib.pyplot as plt

# Please modify these variables with the corresponding files
CONSTRUCTED_FILE = rf'samples/zero-shot-log.txt'
GROUND_TRUTH_FILE = rf'samples/benchmark.dot'
filename = f"samples/mapping/zs-4.1-mini.py" 

module_name = os.path.splitext(os.path.basename(filename))[0] 

spec = importlib.util.spec_from_file_location(module_name, filename)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
graph_mapping = module.mapping

with open(CONSTRUCTED_FILE, 'r', encoding='utf-8') as f:
    content = f.read()
    constructed_g = to_graph(parse_output(content))

with open(GROUND_TRUTH_FILE, 'r') as f:
    content = f.read()
    gt = to_graph(content)

new_constructed = networkx.DiGraph()
new_gt = networkx.DiGraph()

constructed_group_rev_map = {}
gt_group_rev_map = {}
for group in graph_mapping:
    constructed_nodes = group['left']
    gt_nodes = group['right']
    if 'shape' in group:
        shape = group['shape'] 

    if len(constructed_nodes) == 0:
        name = gt_nodes[0]
    else:
        name = constructed_nodes[0]

    for node in constructed_nodes:
        constructed_group_rev_map[node] = name

    for node in gt_nodes:
        gt_group_rev_map[node] = name

    if len(constructed_nodes) != 0:
        new_constructed.add_node(name, shape = shape, name = name)
        
    if len(gt_nodes) != 0:
        new_gt.add_node(name, shape=shape, name = name)

for u, v in constructed_g.edges():
    if constructed_group_rev_map[u] != constructed_group_rev_map[v]:
        new_constructed.add_edge(constructed_group_rev_map[u], constructed_group_rev_map[v])

for u, v in gt.edges():
    if gt_group_rev_map[u] != gt_group_rev_map[v]:
        new_gt.add_edge(gt_group_rev_map[u], gt_group_rev_map[v])


# Node metrics
constructed_entities, constructed_process, constructed_datastore = parse_entities(new_constructed)
gt_entities, gt_process, gt_datastore = parse_entities(new_gt)

constructed_entities_name = [node['name'] for node in constructed_entities]
constructed_process_name = [node['name'] for node in constructed_process]
constructed_datastore_name = [node['name'] for node in constructed_datastore]

gt_entities_name = [node['name'] for node in gt_entities]
gt_process_name = [node['name'] for node in gt_process]
gt_datastore_name = [node['name'] for node in gt_datastore]

common_entities = [node for node in constructed_entities if node['name'] in gt_entities_name]
common_process = [node for node in constructed_process if node['name'] in gt_process_name]
common_datastore = [node for node in constructed_datastore if node['name'] in gt_datastore_name]

if len(constructed_entities) != 0:
    print(f"Entity precision: {len(common_entities) / len(constructed_entities)}")
else: 
    print("Entity precision: 1 (no entities in constructed graph)")

if len(gt_entities) != 0:
    print(f"Entity recall:    {len(common_entities) /          len(gt_entities)}")
else:
    print("Entity recall: 1 (no entities in ground truth graph)")

if len(constructed_process) != 0:
    print(f"Process precision: {len(common_process) / len(constructed_process)}")
else:
    print("Process precision: 1 (no processes in constructed graph)")

if len(gt_process) != 0:
    print(f"Process recall:    {len(common_process) /          len(gt_process)}")
else:
    print("Process recall: 1 (no processes in ground truth graph)")

if len(constructed_datastore) != 0:
    print(f"Datastore precision: {len(common_datastore) / len(constructed_datastore)}")
else:
    print("Datastore precision: 1 (no datastores in constructed graph)")

if len(gt_datastore) != 0:
    print(f"Datastore recall:    {len(common_datastore) /          len(gt_datastore)}")
else:
    print("Datastore recall: 1 (no datastores in ground truth graph)")

# Edge metrics
constructed_edges = new_constructed.edges()
gt_edges = new_gt.edges()
# print(constructed_edges)
# print(gt_edges)

common_edges = [edge for edge in constructed_edges if edge in gt_edges]
# print(f"Common edges: {len(common_edges)}")
# print(gt_group_rev_map, constructed_group_rev_map)
# print(constructed_edges)
# print(gt_edges)

print(f"Edge precision: {len(common_edges) / len(constructed_edges)}")
print(f"Edge recall:    {len(common_edges) /          len(gt_edges)}")

constructed_merge_count = 0
gt_merge_count = 0
for group in graph_mapping:
    if len(group['left']) > 1:
        constructed_merge_count += len(group['left']) - 1
    if len(group['right']) > 1:
        gt_merge_count += len(group['right']) - 1
print(f"Constructed merge count: {constructed_merge_count}")
print(f"GT merge count: {gt_merge_count}")
print(f"Average number of element per group (constructed graph): {constructed_merge_count / len(graph_mapping)}")
print(f"Average number of element per group (constructed graph): {gt_merge_count / len(graph_mapping)}")