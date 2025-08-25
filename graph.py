import pydot
import networkx


s = """digraph DFD {
  rankdir=LR;
  node [fontname="Arial"];

  // Trusted boundary around the application
  subgraph cluster_app {
    label="Trusted Boundary";
    style=dashed;
    MainActivity [shape=circle,label="MainActivity"];
  }

  // External entities
  User [shape=rect,label="User"];
  UIScreen [shape=rect,label="User Interface"];
  WifiService [shape=rect,label="WiFi Service"];
  BTService [shape=rect,label="Bluetooth Service"];
  LocationService [shape=rect,label="Location Service"];
  AccountManager [shape=rect,label="Account Manager"];
  CallLogProvider [shape=rect,label="Call Log Provider"];
  SMSProvider [shape=rect,label="SMS Provider"];
  ContactsProvider [shape=rect,label="Contacts Provider"];
  WebhookServer [shape=rect,label="Webhook Server"];

  // Data flows
  User -> MainActivity [label="Button Click"];
  WifiService -> MainActivity [label="WifiInfo"];
  WifiService -> MainActivity [label="ScanResults"];
  BTService -> MainActivity [label="BluetoothInfo"];
  LocationService -> MainActivity [label="Location Data"];
  AccountManager -> MainActivity [label="Account List"];
  CallLogProvider -> MainActivity [label="Call Log Records"];
  SMSProvider -> MainActivity [label="SMS Messages"];
  ContactsProvider -> MainActivity [label="Contacts List"];
  MainActivity -> WebhookServer [label="Name"];
  WebhookServer -> MainActivity [label="Response"];
  MainActivity -> UIScreen [label="Device Info Report"];
}  
"""

def get_node_key(node_name: str):
	if " " in node_name:
		return f'"{node_name}"'
	else:
		return node_name




def to_graph(dot_code: str):
    graph =  pydot.graph_from_dot_data(dot_code)
    graph = graph[0]
    def flatten_subgraph(sg):
        # Move nodes to the top-level graph
        for node in sg.get_nodes():
            graph.add_node(node)

        # Move edges to the top-level graph
        for edge in sg.get_edges():
            graph.add_edge(edge)

        # Keep track of node names for grouping in the cluster
        node_names = [n.get_name() for n in sg.get_nodes()]

        # Clear the subgraph and keep only node references
        sg.obj_dict["nodes"] = {}
        sg.obj_dict["edges"] = {}
        for name in node_names:
            sg.add_node(pydot.Node(name))

        # Recursively handle nested subgraphs
        for nested in sg.get_subgraphs():
            flatten_subgraph(nested)

    # Flatten every subgraph in the main graph
    for sg in graph.get_subgraphs():
        flatten_subgraph(sg)

    # return graph
    g = networkx.Graph(networkx.nx_pydot.from_pydot(graph))
    for node in g.nodes():
        if g.nodes[node] == {}:
            g.nodes[node]['label'] = node
            g.nodes[node]['shape'] = 'ellipse'
    return g

def insert_mapping(graph, mapping: dict):
    
	for node in graph.nodes():
		graph.nodes[node]['name'] = node
		if node in mapping:
			graph.nodes[node]['mapping'] = mapping[node]
	return graph


def parse_entities(graph):
    # print("hehe")
    print([node for node in graph.nodes() if "shape" not in graph.nodes[node]])
    entities = [graph.nodes[node] for node in graph.nodes() if graph.nodes[node]['shape'] == 'box'] 
    process = [graph.nodes[node] for node in graph.nodes() if graph.nodes[node]['shape'] in ['circle', 'ellipse']]
    datastore = [graph.nodes[node] for node in graph.nodes() if graph.nodes[node]['shape'] == 'cylinder']

    return entities, process, datastore

def similarity(node_name, ground_truth_name):
	return 1

# def match_nodes(node, ground_truth, semantic = SEMANTIC_CHECK):
# 	print(node, ground_truth)
# 	if SEMANTIC_CHECK:
# 		return 	node['shape'] == ground_truth['shape'] \
# 			and node['mapping'] == ground_truth['mapping'] \
# 			and similarity(node['label'], ground_truth['label']) > SEMANTIC_THRESHOLD
# 	try:
# 		return 	node['shape'] == ground_truth['shape'] \
# 			and node['label'] == ground_truth['label']
# 			# and node['mapping'] == ground_truth['mapping'] \
# 	except:
# 		print(ground_truth)


def compare_graph(graph, ground_truth):

	g_edges = graph.edges()
	t_edges = ground_truth.edges

	g_entities, g_process, g_datastore = parse_entities(graph)
	t_entities, t_process, t_datastore = parse_entities(ground_truth)

	print("=" * 40)
	print(g_entities, t_entities)
	print('=' * 40)
	entities_map, common_entities   = map_nodes(g_entities, t_entities, match_nodes)
	process_map, common_process     = map_nodes(g_process, t_process, match_nodes)
	datastore_map, common_datastore = map_nodes(g_datastore, t_datastore, match_nodes)

	node_mapping = {}
	node_mapping.update(entities_map)
	node_mapping.update(process_map)
	node_mapping.update(datastore_map)

	node_accuracy = (common_entities + common_process + common_datastore) / (len(g_entities) + len(g_process) + len(g_datastore))
	node_recall   = (common_entities + common_process + common_datastore) / (len(t_entities) + len(t_process) + len(t_datastore))

	common_edges = []

	for edge in g_edges:
		src, dst = edge
		if (node_mapping.get(src), node_mapping.get(dst)) in t_edges:
			common_edges.append((src, dst))

	edge_accuracy = len(common_edges) / len(g_edges)
	edge_recall   = len(common_edges) / len(t_edges)

	metrics = {
		'node_acc': node_accuracy,
		'node_recall': node_recall,
		'edge_acc': edge_accuracy,
		'edge_recall': edge_recall
	}
	return metrics