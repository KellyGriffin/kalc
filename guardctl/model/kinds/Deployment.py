from guardctl.model.system.Controller import Controller
from guardctl.model.system.base import HasLimitsRequests
from guardctl.model.kinds.Node import Node
from guardctl.model.kinds.PriorityClass import PriorityClass
from guardctl.model.system.Scheduler import Scheduler
import guardctl.model.kinds.Pod as mpod
from guardctl.model.system.primitives import Status
from guardctl.misc.const import STATUS_POD
from poodle import *
from typing import Set
from logzero import logger

class Deployment(Controller, HasLimitsRequests):
    spec_replicas: int
    metadata_name: str
    metadata_namespace: str
    apiVersion: str
    lastPod: "mpod.Pod"
    amountOfActivePods: int
    status: Status
    podList: Set["mpod.Pod"]
    spec_template_spec_priorityClassName: str
    hash: str

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        #TODO fill pod-template-hash with https://github.com/kubernetes/kubernetes/blob/0541d0bb79537431421774465721f33fd3b053bc/pkg/controller/controller_utils.go#L1024
        self.hash = "superhash"


    def hook_after_create(self, object_space):
        
        scheduler = next(filter(lambda x: isinstance(x, Scheduler), object_space))
        deployments = filter(lambda x: isinstance(x, Deployment), object_space)
        for deploymentController in deployments:
            if deploymentController.metadata_name == self.metadata_name:
                message = "Error from server (AlreadyExists): deployments.{0} \"{1}\" already exists").format(self.apiVersion.split("/")[0], self.metadata_name)
                logger.error(message)
                raise message

        for replicaNum in range(self.spec_replicas):
            new_pod = mpod.Pod()
            hash1 = self.hash
            hash2 = str(replicaNum)
            new_pod.metadata_name = str(self.metadata_name) + '-Deployment-' + hash1 + "-" + hash2
            new_pod.toNode = None
            new_pod.cpuRequest = self.cpuRequest
            new_pod.memRequest = self.memRequest
            new_pod.cpuLimit = self.cpuLimit
            new_pod.memLimit = self.memLimit
            new_pod.status = STATUS_POD["Pending"]
            new_pod.hook_after_load(object_space, _ignore_orphan=True) # for service<>pod link
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

