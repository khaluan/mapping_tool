import re
# from config import FORMAT
FORMAT = 'dot'


def parse_output(output: str, format: str = FORMAT) -> str:
    template = f'```{format.lower()}\n(.*?)```'
    # print("[TEMPLATE]: ", template)
    mermaid_code = re.search(template, output, re.DOTALL).group(1)
    return mermaid_code


def parse_mapping(response: str) -> dict:
    pattern = r"^\|\s*(?!-)(.+?)\s*\|\s*(.+?)\s*\|$"

    matches = re.findall(pattern, response, re.MULTILINE)
    graph_mapping = {}

    encoding = False
    elements, files = [], []
    for i, (element, file) in enumerate(matches):
        
        element = element.strip("*")

        elements.append(element)
        files.append(file)
        
    for element, file in zip(elements, files):
        graph_mapping[element] = set(map(lambda txt: txt.strip(), file.split(',')))
    return graph_mapping

response = """
### Data Flow Diagram (DOT)
```dot
digraph DFD {
    "CSV Data Generator" [shape=ellipse];
    "CSV File" [shape=cylinder];
    "CSV Parser" [shape=ellipse];
    "Redis" [shape=cylinder];
    "Publisher" [shape=ellipse];
    "Worker" [shape=ellipse];
    "PostgreSQL" [shape=cylinder];
    "Grafana" [shape=ellipse];

    "CSV Data Generator" -> "CSV File" [label="generate CSV data"];
    "CSV Parser" -> "CSV File" [label="read CSV data"];
    "CSV Parser" -> "Redis" [label="send data"];
    "Publisher" -> "Redis" [label="read data"];
    "Publisher" -> "Worker" [label="send data"];
    "Worker" -> "PostgreSQL" [label="store alerts and indicators"];
    "Grafana" -> "PostgreSQL" [label="query data"];

    // Trust boundary
    subgraph cluster_trusted_boundary {
        style=dashed
        label="Server"
        "CSV Parser"
        "Publisher"
        "Worker"
        "Redis"
        "PostgreSQL"
    }
}
```

### Mapping

| Element                | File(s)                                                                 |
|------------------------|-------------------------------------------------------------------------|
| CSV Data Generator     | data/generate_csv_data.py                                               |
| CSV File               | data/generate_csv_data.py (output file)                                 |
| CSV Parser             | src/gateway/csv_parser.py                                               |
| Redis                  | src/gateway/publisher.py, src/ingress-redis-streams/redis.conf          |
| Publisher              | src/gateway/publisher.py                                                |
| Worker                 | src/worker/src/main.rs, src/worker/src/data_entry.rs, src/worker/src/quantitative_indicators.rs, src/worker/src/postgres_connector.rs |
| PostgreSQL             | src/flyway/sql/V1___initial_schema.sql, src/flyway/sql/V2___create_grafana_db.sql, src/flyway/sql/V4___create_envvar_table.sql |
| Grafana                | src/dashboard/provisioning/datasources/datasources.yaml, src/dashboard/provisioning/dashboards/dashboard.yaml |
===========================================================================================
"""

# dfd_code = parse_output(response)
# mapping = parse_mapping(response)

# from graph import *

# graph = to_graph(dfd_code)
# graph = insert_mapping(graph, mapping)
# metrics = compare_graph(graph, graph)


