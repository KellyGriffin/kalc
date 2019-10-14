from poodle import Object
from guardctl.model.system.primitives import Type, Status
from guardctl.model.kinds.Node import Node


class GlobalVar(Object):
    is_deployment_interrupted: bool
    is_service_interrupted: bool
    is_node_interrupted: bool
    goal_achieved: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_service_interrupted = False
        self.goal_achieved = False
        