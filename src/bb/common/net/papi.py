from Pyro5 import api
from Pyro5.client import Proxy, _RemoteMethod, _StreamResultIterator
from Pyro5.errors import CommunicationError
from Pyro5.protocol import ReceivingMessage
from Pyro5.server import Daemon as PDaemon
from Pyro5.server import expose, oneway

from bb.common.log import Logger

ProxyProperty = ReceivingMessage | _StreamResultIterator | _RemoteMethod | None


def locate_ns() -> Proxy:
    return api.locate_ns()


def invoke(method: ProxyProperty, *args, **kwargs):
    """Runs the method on the remote pyro instance.
    Example usage: invoke(node.add_transaction, register_transaction.to_json())"""
    if isinstance(method, _RemoteMethod):
        return method(*args, **kwargs)
    else:
        raise TypeError(f"{method} could not be invoked, is it a field?")


def get_all_uris_as_dict(prefix: str) -> dict[str, str]:
    ns = locate_ns()
    return invoke(ns.list, prefix)


def get_all_uris(prefix: str) -> list[str]:
    objs = get_all_uris_as_dict(prefix)
    return list(objs.values())


def proxy_of(uri: str) -> Proxy:
    return Proxy(uri)


class Daemon(PDaemon):
    registered_names: list[str] = []

    def __init__(self):
        super().__init__()
        self.log = Logger(self)

    def register(self, obj_or_class: object, ns_name: str):
        """Register an object or class in daemon and nameserver."""
        ns = locate_ns()
        uri = super().register(obj_or_class)
        invoke(ns.register, ns_name, uri)
        self.log.debug(f"registered {ns_name} in ns")
        self.registered_names.append(ns_name)

    def shutdown_with_ns_cleanup(self):
        self.log.info("shutting down...")
        ns = locate_ns()
        for rname in self.registered_names:
            invoke(ns.remove, rname)
            self.log.debug(f"removed {rname} from ns")
        super().shutdown()
        self.log.info("done")

    def start(self):
        self.log.info("starting daemon (Ctrl-C to stop)")
        try:
            super().requestLoop()
        except Exception:
            self.shutdown_with_ns_cleanup()


# re-export
expose
oneway
Proxy
CommunicationError
