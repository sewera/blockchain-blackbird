from bb.common.block import Block
from bb.common.net.papi import expose, oneway
from bb.node.network import Network, Node


class Endpoint:
    def __init__(self, network: Network, node: Node):
        self.network = network
        self.node = node

    @oneway
    @expose
    def upload_transaction(self, transaction_json: str):
        self.network.broadcast("add_transaction", transaction_json)

    @oneway
    @expose
    def commit(self):
        """
        commit synchronizes all the nodes, freezes the transaction list
        in the block, and informs all the nodes to start working for proof
        """
        self.network.broadcast("start_proofing")

    @expose
    def get_last_block(self) -> str:
        return Block().to_json()

    @expose
    def echo(self, s: str) -> str:
        # FIXME: remove this method after testing is done
        return f"echo: {s}"
