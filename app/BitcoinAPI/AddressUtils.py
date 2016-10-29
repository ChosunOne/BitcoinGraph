from blockchain.blockexplorer import *
import networkx

def get_address_alltx(bitcoin_address, max_tx=50, api_code=None):
    """Get data for a single address and the specified number of transactions."""
    
    resource = 'rawaddr/' + bitcoin_address
    if api_code is not None:
        resource += '?api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)

    # Get all the transactions from the given bitcoin address
    offset = 50
    while offset <= json_response['n_tx'] and offset <= max_tx:
        resource = 'rawaddr/' + str(bitcoin_address) + '?offset=' + str(offset)
        response = util.call_api(resource)
        tx_json_response = json.loads(response)
        json_response['txs'] += tx_json_response['txs']
        offset += 50

    return Address(json_response)

def getNextTx(otx, max_tx=50):
    """Get the next outgoing transaction in the chain of transactions"""

    address = get_address_alltx(otx.address, max_tx)
    itx = [x for x in address.transactions if otx.tx_index in [y.tx_index for y in x.inputs]]
    if itx:
        return itx[0]
    else:
        # Max_tx is too small to find the next transaction, kill the branch here
        t = {'tx_index':-1, 'double_spend': False, 'block_height':0, 'time':0, 'relayed_by':0, 'hash':0, 'ver':0, 'size':0, 'inputs':[], 'out':[]}
        tx = Transaction(t)
        tx.tx_index = -1
        return tx

def getIncomingTxs(address, depth_limit=5, input_limit=5):
    """Does a DFS of bitcoin transactions until the miners are found or depth limit reached""" 
    graph = networkx.Graph()
    txQ = []
    visited = []
    indexes = []

    graph.add_node(address.address, title=address.address)
    for tx in address.transactions:
        if address.address in [x.address for x in tx.outputs]:
            txQ.append((tx, 0))
            indexes.append(address.address)

    while len(txQ) > 0:
        tx, depth = txQ.pop()
        index = indexes.pop()
        if tx in visited:
            continue
        else:   
            visited.append(tx)

        # Trim inputs to the x largest inputs
        inputs = [x for x in tx.inputs if hasattr(x, "value")]
        inputs.sort(key=lambda x: x.value, reverse=True)
        inputs = [x for x in tx.inputs if not hasattr(x, "value")] + inputs
        inputs = inputs[:input_limit]

        for itx in inputs:
            if not (depth >= depth_limit or not hasattr(itx, "tx_index")):
                graph.add_node(itx.tx_index, title=itx.tx_index)
                edge = (itx.tx_index, index)
                graph.add_edge(*edge)

                graph[edge[0]][edge[1]]['value'] = itx.value
                graph[edge[0]][edge[1]]['color'] = '#32cd32'

                itx_ent = get_tx(str(itx.tx_index))
                txQ.append((itx_ent, depth + 1))
                indexes.append(itx.tx_index)

    return graph
        
def getOutgoingTxs(address, depth_limit=5, output_limit=5, max_tx=50):
    """Does a DFS of bitcoin transactions until the final address or depth limit is reached"""
    graph = networkx.Graph()
    txQ = []
    visited = []
    addresses = []
    
    graph.add_node(address.address, title=address.address)
    for tx in address.transactions:
        if address.address in [x.address for x in tx.inputs if hasattr(x, "address")]:
            txQ.append((tx, 0))
            addresses.append(address.address)

    while len(txQ) > 0:
        tx, depth = txQ.pop()
        addr = addresses.pop()
        if tx in visited:
            continue

        visited.append(tx)

        # Trim outputs to the x largest transactions
        outputs = [x for x in tx.outputs]
        outputs.sort(key=lambda x: x.value, reverse=True)
        outputs = outputs[:output_limit]

        for otx in outputs:
            if not (depth >= depth_limit or not otx.spent):
                graph.add_node(otx.address, title=otx.tx_index)
                edge = (addr, otx.address)
                graph.add_edge(*edge)
                
                graph[edge[0]][edge[1]]['value'] = otx.value
                graph[edge[0]][edge[1]]['color'] = '#FF0000'
                
                otx_ent =  getNextTx(otx, max_tx)
                if otx_ent.tx_index > 0:
                    txQ.append((otx_ent, depth + 1))
                    addresses.append(otx.address)

    return graph
        
        