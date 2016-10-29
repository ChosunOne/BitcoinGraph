Bitcoin Graph Documentation
By Josiah Evans

#Dependencies:  
        Django (1.10.2)
		Blockchain (1.3.3) – For retrieving address and transactions
		Decorator (4.0.10)
		Networkx (1.11) – For representing the graphs
		Pip (8.1.1)
		Setuptools (20.10.1)

#Usage:  
Visit https://bitcoingraph.herokuapp.com to start using the app.

Specify the Bitcoin Address, maximum number of transactions, maximum depth, and maximum branching for the graph and hit load.  You may need to wait a few minutes depending on the given parameters (this is due to many api calls to blockchain.info).  

When the graph loads, the larger circle represents the address you have specified.  The other circles represent transactions of bitcoins that have gone through the specified address.  Green links indicate they are moving bitcoins toward the specified address, and red links indicate bitcoins moving away from the specified address.  The width of the links between transactions represents the value of the transaction.  Specifically, the thickness indicates the order of magnitude of the value.

Unconfirmed transactions will not be displayed as the api used to retrieve transactions only finds confirmed transactions.

Hovering over a circle will display the transaction index of the circle.  You can verify the accuracy of the graph by going to https://blockchain.info/tx/ and appending the transaction index to the end of that url.  For example, if your transaction index is 182942555, you can visit https://blockchain.info/tx/182942555 to see the transaction details.  

#Structure

The code is structured as a Django web app, with most of the logic being contained in the “BitcoinAPI” folder inside of the root app folder in the “AddressUtils.py” file.  The “views.py” file in the root app folder calls the functions from AddressUtils to create the incoming and outgoing graphs, and composes them together.  After composition, it renames the ids of the graph so that they are correctly displayed in graph.js, in static/app/scripts.   

Technical Annotation

    AddressUtils.py
This file is home to four functions, two for retrieving transactions from addresses and two for creating the graphs.  

	get_address_alltx(bitcoin_address, max_tx=50, api_code=None)
This function is a slight rewrite of the get_address function in the blockchain api module blockexplorer.  The modification is the introduction of max_tx, which allows you to retrieve more than 50 transactions from the requested address (though the default limit is 50).

    getNextTx(otx, max_tx=50)
This function serves to get the transaction where the given transaction (otx) is an input.  	
It requests transaction from the receiving address and attempts to match an input with the given transaction.  If it cannot find a match, then likely the max_tx limiter is too small, and so it returns a dummy transaction with an index of -1 so the calling function can know the next transaction could not be found.  

    getIncomingTxs(address, depth_limit=5, input_limit=5)
This function does a depth first search of all of the incoming transactions to the given address, and returns a graph of the search.  The search continues until the depth limit is reached or the transaction contains newly mined coins.  The input limit limits the number of incoming transactions to explore such that the largest x transactions are explored.  Properties of each transaction are stored in graph nodes and edges for display in the browser.  The graph itself is represented by a networkx graph object.

    getOutgoingTxs(address, depth_limit=5, input_limit=5, max_tx=50)
This function behaves very similarly to getIncomingTxs, but requires the extra argument for the getNextTx function.  This is because while incoming transactions contain the transaction index of the input transaction, an outgoing transaction does not contain the next transaction that uses its output, thus finding the outgoing transactions is slightly slower than finding the incoming ones.  

    graph.js
This file is responsible for displaying the graph of the transactions and given address.  It relies on d3.js and the type of graph displayed is a directed force graph.  This enables you to move the nodes around to better understand the connections between nodes.  The graph is represented by an updated svg on the page.
