from typing import Set
from guardctl.model.system.primitives import Label, StatusServ
from guardctl.model.kinds.Node import Node
from guardctl.model.system.base import HasLabel
import guardctl.model.kinds.Pod as mpod
from guardctl.model.system.primitives import StatusSched
from guardctl.misc.const import *


class Service(HasLabel):
    spec_selector: Set[Label]
    lastPod: "mpod.Pod"
    atNode: Node
    amountOfActivePods: int
    status: StatusServ
    metadata_name: str
    searchable: bool
    
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.amountOfActivePods = 0
        self.status = STATUS_SERV["Pending"]
        self.searchable = True
 

    # def __repr__(self):
    #     return 'Servicename : ' + str(self._get_value()) 

Service.SERVICE_NULL = Service("NULL")
