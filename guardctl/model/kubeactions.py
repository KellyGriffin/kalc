import sys
from poodle import planned
from logzero import logger
from guardctl.model.system.base import HasLimitsRequests, HasLabel
from guardctl.model.system.Scheduler import Scheduler
from guardctl.model.system.globals import GlobalVar
from guardctl.model.system.primitives import TypeServ
from guardctl.model.system.Controller import Controller
from guardctl.model.system.primitives import Label
from guardctl.model.kinds.Service import Service
from guardctl.model.kinds.Deployment import Deployment
from guardctl.model.kinds.Pod import Pod
from guardctl.model.kinds.Node import Node
from guardctl.model.kinds.PriorityClass import PriorityClass, zeroPriorityClass
from guardctl.model.scenario import ScenarioStep, describe
from guardctl.misc.const import *
from guardctl.misc.problem import ProblemTemplate
from guardctl.misc.util import cpuConvertToAbstractProblem, memConvertToAbstractProblem

class KubernetesModel(ProblemTemplate):
    def problem(self):
        self.scheduler = next(filter(lambda x: isinstance(x, Scheduler), self.objectList))
        self.globalVar = next(filter(lambda x: isinstance(x, GlobalVar), self.objectList))

    @planned(cost=100)
    def Mark_service_as_started(self,
                service1: Service,
                scheduler: "Scheduler"
            ):
        assert service1.amountOfActivePods > 0
        service1.status = STATUS_SERV["Started"]

        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Mark service as started",
            parameters={},
            probability=1.0,
            affected=[describe(service1)]
        )

    @planned(cost=100)
    def SetDefaultMemRequestForPod(self,
        pod1: "Pod",
        memLimit: int
        ):
            assert pod1.memRequest == -1
            assert pod1.memLimit > -1
            assert memLimit == pod1.memLimit

            pod1.memRequest = memLimit

            return ScenarioStep(
                name=sys._getframe().f_code.co_name,
                subsystem=self.__class__.__name__,
                description="Setting default memory request for pod",
                parameters={"currentMemoryRequest": -1, "newMemoryRequest": str(pod1.memLimit)},
                probability=1.0,
                affected=[describe(pod1)]
            )

    @planned(cost=100)
    def SetDefaultCpuRequestForPod(self,
        pod1: "Pod",
        cpuLimit: int
        ):
            assert pod1.cpuLimit > -1
            assert pod1.cpuRequest == -1
            assert cpuLimit == pod1.cpuLimit

            pod1.cpuRequest = cpuLimit

            return ScenarioStep(
                name=sys._getframe().f_code.co_name,
                subsystem=self.__class__.__name__,
                description="Setting default cpu request for pod",
                parameters={"currentCpuRequest": -1, "newCpuRequest": str(pod1.cpuLimit)},
                probability=1.0,
                affected=[describe(pod1)]
            )

    @planned(cost=100)
    def SetDefaultMemLimitForPod(self,
        pod1: "Pod",
        node: "Node" ,
        memCapacity: int
        ):
            assert pod1.memLimit == -1
            assert node == pod1.atNode
            assert memCapacity == node.memCapacity
            pod1.memLimit = memCapacity

            return ScenarioStep(
                name=sys._getframe().f_code.co_name,
                subsystem=self.__class__.__name__,
                description="Setting default memory limit for pod",
                parameters={"currentMemoryLimit": -1, "newMemoryLimit": str(pod1.memLimit)},
                probability=1.0,
                affected=[describe(pod1)]
            )

    @planned(cost=100)
    def SetDefaultCpuLimitForPod(self,
        pod1: "Pod",
        node: "Node" ,
        cpuCapacity: int
        ):
            assert pod1.cpuLimit == -1
            assert node == pod1.atNode
            assert cpuCapacity == node.cpuCapacity

            pod1.cpuLimit = cpuCapacity

            return ScenarioStep(
                name=sys._getframe().f_code.co_name,
                subsystem=self.__class__.__name__,
                description="Setting default cpu limit for pod to node capacity",
                parameters={"currentCpuLimit": -1, "newCpuLimit": str(pod1.cpuLimit)},
                probability=1.0,
                affected=[describe(pod1)]
            )

    @planned(cost=100)
    def SetDefaultMemLimitForPodBeforeNodeAssignment(self,
        pod1: "Pod",
        node: "Node" ,
        memCapacity: int
        ):
            assert pod1.memLimit == -1
            assert memCapacity == node.memCapacity
            pod1.toNode = node
            pod1.memLimit = memCapacity

            return ScenarioStep(
                name=sys._getframe().f_code.co_name,
                subsystem=self.__class__.__name__,
                description="no description provided",
                parameters={},
                probability=1.0,
                affected=[describe(pod1)]
            )

    @planned(cost=100)
    def SetDefaultCpuLimitForPodBeforeNodeAssignment(self,
        pod1: "Pod",
        node: "Node" ,
        cpuCapacity: int):
            assert pod1.cpuLimit == -1
            assert cpuCapacity == node.cpuCapacity
            pod1.toNode = node
            pod1.cpuLimit = cpuCapacity

            return ScenarioStep(
                name=sys._getframe().f_code.co_name,
                subsystem=self.__class__.__name__,
                description="no description provided",
                parameters={},
                probability=1.0,
                affected=[describe(pod1)]
            )

    @planned(cost=100)
    def Evict_and_replace_less_prioritized_pod_when_target_node_is_not_defined(self,
                podPending: "Pod",
                podToBeReplaced: "Pod",
                node: "Node" , # unused
                scheduler: "Scheduler",
                priorityClassOfPendingPod: PriorityClass,
                priorityClassOfPodToBeReplaced: PriorityClass
                ):
        assert podPending in scheduler.podQueue
        assert podPending.toNode == Node.NODE_NULL
        assert podPending.status == STATUS_POD["Pending"]
        assert priorityClassOfPendingPod == podPending.priorityClass
        assert priorityClassOfPodToBeReplaced ==  podToBeReplaced.priorityClass
        # assert preemptionPolicyOfPendingPod == priorityClassOfPendingPod.preemptionPolicy
        # assert preemptionPolicyOfPodToBeReplaced == priorityClassOfPodToBeReplaced.preemptionPolicy
        # assert priorityClassOfPendingPod.preemptionPolicy == self.constSymbol["PreemptLowerPriority"]
        assert priorityClassOfPendingPod.priority > priorityClassOfPodToBeReplaced.priority
        assert podToBeReplaced.status == STATUS_POD["Running"]
        podToBeReplaced.status = STATUS_POD["Killing"]

        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Because pod has lower priority, it is getting evicted to make room for new pod",
            parameters={"podPending": describe(podPending), "podToBeReplaced": describe(podToBeReplaced)},
            probability=1.0,
            affected=[describe(podPending), describe(podToBeReplaced)]
        )

    @planned(cost=100)
    def Evict_and_replace_less_prioritized_pod_when_target_node_is_defined(self,
                podPending: "Pod",
                podToBeReplaced: "Pod",
                nodeForPodPending: "Node" ,
                scheduler: "Scheduler",
                priorityClassOfPendingPod: PriorityClass,
                priorityClassOfPodToBeReplaced: PriorityClass
                ):
        assert podPending in scheduler.podQueue
        assert podPending.toNode == nodeForPodPending
        assert nodeForPodPending.isNull == False
        assert podToBeReplaced.atNode == nodeForPodPending
        assert podPending.status == STATUS_POD["Pending"]
        assert priorityClassOfPendingPod == podPending.priorityClass
        assert priorityClassOfPodToBeReplaced ==  podToBeReplaced.priorityClass
        # assert preemptionPolicyOfPendingPod == priorityClassOfPendingPod.preemptionPolicy
        # assert preemptionPolicyOfPodToBeReplaced == priorityClassOfPodToBeReplaced.preemptionPolicy
        # assert priorityClassOfPendingPod.preemptionPolicy == self.constSymbol["PreemptLowerPriority"]
        assert priorityClassOfPendingPod.priority > priorityClassOfPodToBeReplaced.priority
        assert podToBeReplaced.status == STATUS_POD["Running"]
        podToBeReplaced.status = STATUS_POD["Killing"]

        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Because pod has lower priority, it is getting evicted to make room for new pod",
            parameters={"podPending": describe(podPending), "podToBeReplaced": describe(podToBeReplaced)},
            probability=1.0,
            affected=[describe(podPending), describe(podToBeReplaced)]
        )
        
    @planned(cost=100)
    def Mark_Pod_As_Exceeding_Mem_Limits(self, podTobeKilled: "Pod",nodeOfPod: "Node" ):
        assert podTobeKilled.memLimitsStatus == STATUS_LIM["Limit Met"]
        assert nodeOfPod == podTobeKilled.atNode
        assert podTobeKilled.memLimit <  podTobeKilled.currentRealMemConsumption
        nodeOfPod.AmountOfPodsOverwhelmingMemLimits += 1
        podTobeKilled.memLimitsStatus = STATUS_LIM["Limit Exceeded"]

        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="no description provided",
            parameters={},
            probability=1.0,
            affected=[]
        )

    @planned(cost=100)
    def Mark_Pod_As_Not_Exceeding_Mem_Limits(self, podTobeReanimated: "Pod",
        nodeOfPod: "Node"
        #, globalVar1: GlobalVar
        ):
        assert nodeOfPod == podTobeReanimated.atNode
        assert podTobeReanimated.memLimitsStatus == STATUS_LIM["Limit Exceeded"]
        assert nodeOfPod == podTobeReanimated.atNode
        assert podTobeReanimated.memLimit >  podTobeReanimated.currentRealMemConsumption
        nodeOfPod.AmountOfPodsOverwhelmingMemLimits -= 1
        podTobeReanimated.memLimitsStatus = STATUS_LIM["Limit Met"]

        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="no description provided",
            parameters={},
            probability=1.0,
            affected=[]
        )

    @planned(cost=100)
    def MemoryErrorKillPodExceedingLimits(self,
        nodeOfPod: "Node" ,
        pod1TobeKilled: "Pod"
        ):
        assert pod1TobeKilled.atNode == nodeOfPod
        assert nodeOfPod.memCapacity < nodeOfPod.currentRealMemConsumption
        assert pod1TobeKilled.memLimitsStatus == STATUS_LIM["Limit Exceeded"]
        pod1TobeKilled.status = STATUS_POD["Killing"]

        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="no description provided",
            parameters={},
            probability=1.0,
            affected=[]
        )

    @planned(cost=100)
    def MemoryErrorKillPodNotExceedingLimits(self,
        nodeOfPod: "Node" ,
        podTobeKilled: "Pod"):
        assert podTobeKilled.atNode == nodeOfPod
        assert nodeOfPod.memCapacity < nodeOfPod.currentRealMemConsumption
        assert podTobeKilled.memLimitsStatus == STATUS_LIM["Limit Met"]

        podTobeKilled.status = STATUS_POD["Killing"]

        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="no description provided",
            parameters={},
            probability=1.0,
            affected=[]
        )

    @planned(cost=100)
    def KillPod(self,
            podBeingKilled : "Pod",
            nodeWithPod : "Node" ,
            serviceOfPod: "Service",
            # globalVar1: "GlobalVar",
            scheduler: "Scheduler",
            amountOfActivePodsPrev: int

         ):
        assert podBeingKilled.atNode == nodeWithPod
        assert podBeingKilled.targetService == serviceOfPod
        assert podBeingKilled.status ==  STATUS_POD["Killing"]
        # assert podBeingKilled.amountOfActiveRequests == 0 #For Requests
        assert amountOfActivePodsPrev == serviceOfPod.amountOfActivePods

        nodeWithPod.currentFormalMemConsumption -= podBeingKilled.memRequest
        nodeWithPod.currentFormalCpuConsumption -= podBeingKilled.cpuRequest
        serviceOfPod.amountOfActivePods -= 1
        podBeingKilled.status =  STATUS_POD["Pending"]
        scheduler.podQueue.add(podBeingKilled)
        scheduler.status = STATUS_SCHED["Changed"]

        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Killing pod",
            parameters={"podBeingKilled": describe(podBeingKilled)},
            probability=1.0,
            affected=[describe(podBeingKilled)]
        )

    @planned(cost=100)
    def SelectNode(self, 
        pod1: "Pod",
        SelectedNode: "Node" ):
        assert pod1.toNode == Node.NODE_NULL
        pod1.toNode = SelectedNode
        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Selected node for pod placement",
            parameters={"pod": describe(pod1), "node": describe(SelectedNode)},
            probability=1.0,
            affected=[describe(pod1), describe(SelectedNode)]
        )

    @planned(cost=10)
    def StartPod(self, 
        podStarted: "Pod",
        node: "Node" ,
        scheduler: "Scheduler",
        serviceTargetForPod: "mservice.Service"
        ):

        assert podStarted in scheduler.podQueue
        assert podStarted.toNode == node
        assert podStarted.targetService == serviceTargetForPod
        assert podStarted.cpuRequest > -1
        assert podStarted.memRequest > -1
        assert node.currentFormalCpuConsumption + podStarted.cpuRequest <= node.cpuCapacity
        assert node.currentFormalMemConsumption + podStarted.memRequest <= node.memCapacity

        node.currentFormalCpuConsumption += podStarted.cpuRequest
        node.currentFormalMemConsumption += podStarted.memRequest
        podStarted.atNode = node        
        scheduler.queueLength -= 1
        scheduler.podQueue.remove(podStarted)
 
        serviceTargetForPod.amountOfActivePods += 1
        podStarted.status = STATUS_POD["Running"] 
        serviceTargetForPod.status = STATUS_SERV["Started"]
        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Starting pod",
            parameters={"podStarted": describe(podStarted)},
            probability=1.0,
            affected=[describe(podStarted), describe(node)]
        )
    
    @planned(cost=10)
    def StartPod_IF_hasService_isNull(self, 
        podStarted: "Pod",
        node: "Node" ,
        scheduler: "Scheduler"
        ):
#TODO: add assert - service is null and other branching
        assert podStarted in scheduler.podQueue
        assert podStarted.toNode == node
        assert podStarted.cpuRequest > -1
        assert podStarted.memRequest > -1
        assert node.currentFormalCpuConsumption + podStarted.cpuRequest <= node.cpuCapacity 
        assert node.currentFormalMemConsumption + podStarted.memRequest <= node.memCapacity

        node.currentFormalCpuConsumption += podStarted.cpuRequest
        node.currentFormalMemConsumption += podStarted.memRequest
        podStarted.atNode = node        
        scheduler.queueLength -= 1
        scheduler.podQueue.remove(podStarted)
        podStarted.status = STATUS_POD["Running"] 
        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Starting pod",
            parameters={"podStarted": describe(podStarted)},
            probability=1.0,
            affected=[describe(podStarted), describe(node)]
        )

    @planned(cost=30000)
    def Scheduler_cant_place_pod(self, scheduler: "Scheduler"):
        scheduler.queueLength -= 1
        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Can't place a pod",
            parameters={},
            probability=1.0,
            affected=[]
        )

        #todo: Soft conditions are not supported yet ( prioritization of nodes :  for example healthy  nodes are selected  rather then non healthy if pod  requests such behavior 
    
    @planned(cost=100)
    def ScheduleQueueProcessed(self, scheduler: "Scheduler"):
        assert  scheduler.queueLength == 0
        scheduler.status = STATUS_SCHED["Clean"]
        return ScenarioStep(
            name=sys._getframe().f_code.co_name,
            subsystem=self.__class__.__name__,
            description="Finished processing pod queue",
            parameters={},
            probability=1.0,
            affected=[]
        )