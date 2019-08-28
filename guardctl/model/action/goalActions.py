from poodle import planned
from guardctl.model.object.k8s_classes import *

class K8GoalActions:
    @planned
    def MarkServiceOutageEvent(self,
    service1: Service,
    pod1: Pod,
    globalVar1: GlobalVar,
    scheduler1: Scheduler,
    currentFormalCpuConsumptionLoc: int,
    currentFormalMemConsumptionLoc: int,
    cpuRequestLoc: int,
    memRequestLoc: int
    ):
        assert scheduler1.status == STATUS_SCHED_CLEAN 
        assert service1.amountOfActivePods == 0
        assert service1.status == STATUS_SERV_STARTED
        assert pod1.targetService == service1
        assert globalVar1.currentFormalCpuConsumption == currentFormalCpuConsumptionLoc
        assert globalVar1.currentFormalMemConsumption == currentFormalMemConsumptionLoc
        assert pod1.cpuRequest == cpuRequestLoc
        assert pod1.memRequest == memRequestLoc
        assert globalVar1.currentFormalCpuConsumption + pod1.cpuRequest < globalVar1.cpuCapacity + 1
        assert globalVar1.currentFormalMemConsumption + pod1.memRequest < globalVar1.memCapacity  + 1

        service1.status = STATUS_SERV_INTERRUPTED
    

    
    @planned(cost=10000)
    def UnsolveableServiceStart(self,
    service1: Service,
    scheduler1: Scheduler
    ):
        assert scheduler1.status == STATUS_SCHED_CHANGED
        service1.status = STATUS_SERV_STARTED