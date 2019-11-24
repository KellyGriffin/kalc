from poodle import Object
from guardctl.model.system.primitives import Type, Status

class GlobalVar(Object):
    is_deployment_disrupted: bool
    is_deployment_distuption_searchable: bool
    is_service_disrupted: bool
    is_service_disruption_searchable: bool
    is_node_disrupted: bool
    amountOfNodes: int
    amountOfNodesDisrupted: int
    limitOfAmountOfNodesDisrupted: int
    is_node_disruption_searchable: bool
    is_daemonset_disrupted: bool
    is_daemonset_distuption_searchable: bool
    goal_achieved: bool
    block_node_outage_in_progress: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_service_disrupted = False
        self.is_deployment_disrupted = False
        self.is_daemonset_disrupted = False
        self.is_node_disrupted = False
        self.goal_achieved = False
        self.is_deployment_distuption_searchable = True
        self.is_service_disruption_searchable = True
        self.is_node_disruption_searchable = True
        self.is_daemonset_distuption_searchable = True
        self.amountOfNodes = 0
        self.amountOfNodesDisrupted = 0
        self.block_node_outage_in_progress = False
        