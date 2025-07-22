import matplotlib.pyplot as plt
import networkx as nx
import tempfile


def generate_full_network_graph(domain, ips, open_ports, server_info):
    G = nx.Graph()
    G.add_node(domain, color='red')

    for ip in ips:
        G.add_node(ip, color='green')
        G.add_edge(domain, ip)

        ports = open_ports.get(ip, [])
        for port in ports:
            port_node = f"{ip}:{port}"
            G.add_node(port_node, color='blue')
            G.add_edge(ip, port_node)

        info = server_info.get(ip, {})
        isp = info.get("ISP")
        city = info.get("City")
        if isp:
            isp_node = f"{ip} ISP: {isp}"
            G.add_node(isp_node, color='orange')
            G.add_edge(ip, isp_node)
        if city:
            city_node = f"{ip} City: {city}"
            G.add_node(city_node, color='purple')
            G.add_edge(ip, city_node)

    colors = [G.nodes[n].get('color', 'gray') for n in G.nodes()]
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=900, font_size=8, edge_color='gray')

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp_file.name)
    plt.close()

    return temp_file.name
