"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext

from app.BitcoinAPI.AddressUtils import *
from blockchain.blockexplorer import *
from datetime import datetime
from networkx.readwrite.json_graph import *
import json

def home(request, bitcoin_address=0, max_tx=50, depth_limit=5, branch_limit=5):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    max_tx = int(max_tx)
    depth_limit = int(depth_limit)
    branch_limit = int(branch_limit)

    root_address = {}
    ingraph = None
    outgraph = None
    graph = None
    graph_data = None
    graph_json = ''

    if bitcoin_address != 0:
        root_address = get_address_alltx(bitcoin_address, max_tx)

    if root_address:
        ingraph = getIncomingTxs(root_address, depth_limit, branch_limit)
        outgraph = getOutgoingTxs(root_address, depth_limit, branch_limit, max_tx)

    if ingraph:
        graph = networkx.compose(ingraph, outgraph)

    if graph:
        graph_data = node_link_data(graph)
        graph_data['links'] = [
        {
            'source': graph_data['nodes'][link['source']]['id'],
            'target': graph_data['nodes'][link['target']]['id'],
            'value': link['value'],
            'color': link['color']
        }
        for link in graph_data['links']]
        graph_json = json.dumps(graph_data)

    return render(
        request,
        'index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'bitcoin_address': bitcoin_address,
            'graph_json': graph_json,
            'max_tx': max_tx,
            'depth_limit': depth_limit,
            'branch_limit': branch_limit
        }
    )
