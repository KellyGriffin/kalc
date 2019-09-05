from guardctl.model.system.Controller import Controller
from guardctl.model.system.base import HasLimitsRequests
from guardctl.model.kinds.Node import Node
from guardctl.model.kinds.PriorityClass import PriorityClass
from guardctl.model.system.Scheduler import Scheduler
import guardctl.model.kinds.Pod as mpod
from guardctl.model.system.primitives import Status
from guardctl.misc.const import *
from poodle import *
from typing import Set
from logzero import logger

class DaemonSet(Controller, HasLimitsRequests):
    lastPod: "mpod.Pod"
    amountOfActivePods: int
    status: Status
    podList: Set["mpod.Pod"]
    spec_template_spec_priorityClassName: str


    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

    def hook_after_create(self, object_space):
        nodes = filter(lambda x: isinstance(x, Node), object_space)
        scheduler = next(filter(lambda x: isinstance(x, Scheduler), object_space))
        i = 0
        for node in nodes:
            i += 1
            new_pod = mpod.Pod()
            new_pod.metadata_name = str(self.metadata_name) + '-DaemonSet_CR-' + str(i)
            new_pod.toNode = node
            new_pod.cpuRequest = self.cpuRequest
            new_pod.memRequest = self.memRequest
            new_pod.cpuLimit = self.cpuLimit
            new_pod.memLimit = self.memLimit
            new_pod.status = STATUS_POD["Pending"]
            try:
                new_pod.priorityClass = \
                    next(filter(\
                        lambda x: \
                            isinstance(x, PriorityClass) and \
                            str(x.metadata_name) == str(self.spec_template_spec_priorityClassName),\
                        object_space))
            except StopIteration:
                logger.warning("Could not reference priority class")
            self.podList.add(new_pod)
            object_space.append(new_pod)
            scheduler.podQueue.add(new_pod)
            scheduler.queueLength += 1
            scheduler.status = STATUS_SCHED["Changed"]

