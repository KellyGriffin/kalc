from tests.test_util import print_objects
from guardctl.model.search import AnyGoal 
from guardctl.model.system.Scheduler import Scheduler
from guardctl.model.system.globals import GlobalVar
from guardctl.model.kinds.Service import Service
from guardctl.model.kinds.Node import Node
from guardctl.model.kinds.Pod import Pod
from guardctl.model.kinds.Deployment import Deployment
from guardctl.model.kinds.DaemonSet import DaemonSet
from guardctl.model.kinds.PriorityClass import PriorityClass
from guardctl.model.kubernetes import KubernetesCluster
from guardctl.misc.const import *
import pytest
from guardctl.model.search import K8ServiceInterruptSearch
from guardctl.misc.object_factory import labelFactory
from click.testing import CliRunner
from tests.test_util import print_objects
from guardctl.model.scenario import Scenario
from poodle import planned

def build_running_pod(podName, cpuRequest, memRequest, atNode):
    pod_running_1 = Pod()
    pod_running_1.metadata_name = "pod"+str(podName)
    pod_running_1.cpuRequest = 2
    pod_running_1.memRequest = 2
    pod_running_1.atNode = atNode
    pod_running_1.status = STATUS_POD["Running"]
    pod_running_1.hasDeployment = False
    pod_running_1.hasService = False
    pod_running_1.hasDaemonset = False
    return pod_running_1

def build_running_pod_with_d(podName, cpuRequest, memRequest, atNode, d, ds):
    pod_running_1 = Pod()
    pod_running_1.metadata_name = "pod"+str(podName)
    pod_running_1.cpuRequest = cpuRequest
    pod_running_1.memRequest = memRequest
    pod_running_1.atNode = atNode
    pod_running_1.status = STATUS_POD["Running"]
    pod_running_1.hasDeployment = False
    pod_running_1.hasService = False
    pod_running_1.hasDaemonset = False
    if d is not None:
        d.podList.add(pod_running_1)
        d.amountOfActivePods += 1
        pod_running_1.hasDeployment = True
    if ds is not None:
        ds.podList.add(pod_running_1)
        ds.amountOfActivePods += 1
        pod_running_1.hasDaemonset = True
    atNode.currentFormalCpuConsumption += cpuRequest
    atNode.currentFormalMemConsumption += memRequest
    return pod_running_1

 


def build_pending_pod(podName, cpuRequest, memRequest, toNode):
    p = build_running_pod(podName, cpuRequest, memRequest, Node.NODE_NULL)
    p.status = STATUS_POD["Pending"]
    p.toNode = toNode
    p.hasDeployment = False
    p.hasService = False
    p.hasDaemonset = False
    return p

def build_pending_pod_with_d(podName, cpuRequest, memRequest, toNode, d, ds):
    p = Pod()
    p.metadata_name = "pod"+str(podName)
    p.cpuRequest = cpuRequest
    p.memRequest = memRequest
    p.status = STATUS_POD["Pending"]
    p.hasDeployment = False
    p.hasService = False
    p.hasDaemonset = False
    if d is not None:
        d.podList.add(p)
        p.hasDeployment = True
    if ds is not None:
        ds.podList.add(p)
        p.hasDaemonset = True
        p.toNode = toNode
    return p

 
def test_run_pods_no_eviction():
    # TODO: extract final status for loader unit tests from here
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    n.currentFormalCpuConsumption = 0
    n.currentFormalMemConsumption = 0

    # priority - as needed
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Pedning pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    # Create a "holding" controller - optional
    ds = DaemonSet()
    ds.podList.add(pod_pending_1)
    ds.amountOfActivePods = 0
    pod_pending_1.hasDaemonset = True


    k.state_objects.extend([n, pc, pod_pending_1, ds])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    p.run(timeout=150)
    # TODO: fix strange behaviour -->>
    # assert "StartPod" in "\n".join([x() for x in p.plan])
    assert "StartPod" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
    #     print(a) 


def test_run_pods_with_eviction():
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
    n.isNull = False

    # Create running pods
    pod_running_1 = build_running_pod(1,2,2,n)
    pod_running_2 = build_running_pod(2,2,2,n)

    ## Set consumptoin as expected
    n.currentFormalCpuConsumption = 4
    n.currentFormalMemConsumption = 4

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, pod_pending_1])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    p.run(timeout=150)
    assert "StartPod" in "\n".join([repr(x) for x in p.plan])
    assert "Evict" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
        # print(a)


def test_synthetic_service_outage():
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
    n.isNull = False

    # Create running pods
    pod_running_1 = build_running_pod(1,2,2,n)
    pod_running_2 = build_running_pod(2,2,2,n)

    ## Set consumptoin as expected
    n.currentFormalCpuConsumption = 4
    n.currentFormalMemConsumption = 4

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 1
    s.status = STATUS_SERV["Started"]

    # our service has only one pod so it can detect outage
    #  (we can't evict all pods here with one)
    pod_running_1.targetService = s
    pod_running_1.hasService = True

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, pod_pending_1])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        pass
        # goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    p.run(timeout=150)
    assert "StartPod" in "\n".join([repr(x) for x in p.plan])
    assert "Evict" in "\n".join([repr(x) for x in p.plan])
    assert "MarkServiceOutageEvent" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
        # print(a)

def construct_multi_pods_eviction_problem():
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
    n.isNull = False

    # Create running pods
    pod_running_1 = build_running_pod(1,2,2,n)
    pod_running_2 = build_running_pod(2,2,2,n)

    ## Set consumptoin as expected
    n.currentFormalCpuConsumption = 4
    n.currentFormalMemConsumption = 4

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has only one pod so it can detect outage
    #  (we can't evict all pods here with one)
    # TODO: no outage detected if res is not 4
    pod_running_1.targetService = s
    pod_running_2.targetService = s

    pod_running_1.hasService = True
    pod_running_2.hasService = True

    # Pending pod
    pod_pending_1 = build_pending_pod(3,4,4,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, pod_pending_1,s])
    # print_objects(k.state_objects)
    return k

def test_synthetic_service_outage_multi():
    "Multiple pods are evicted from one service to cause outage"
    k = construct_multi_pods_eviction_problem()
    class NewGOal(AnyGoal):
        pass
        # goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    p.run(timeout=250)
    assert "StartPod" in "\n".join([repr(x) for x in p.plan])
    assert "Evict" in "\n".join([repr(x) for x in p.plan])
    assert "MarkServiceOutageEvent" in "\n".join([repr(x) for x in p.plan])
    for a in p.plan:
        print(a)

# @pytest.mark.skip(reason="FIXME - this test fails because of a bug in the model")
def test_synthetic_service_NO_outage_multi():
    "No outage is caused by evicting only one pod of a multi-pod service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
    n.isNull = False

    # Create running pods
    pod_running_1 = build_running_pod(1,2,2,n)
    pod_running_2 = build_running_pod(2,2,2,n)

    ## Set consumptoin as expected
    n.currentFormalCpuConsumption = 4
    n.currentFormalMemConsumption = 4

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has only one pod so it can detect outage
    #  (we can't evict all pods here with one)
    # TODO: no outage detected if res is not 4
    pod_running_1.targetService = s
    pod_running_2.targetService = s

    pod_running_1.hasService = True
    pod_running_2.hasService = True
    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, pod_pending_1,s])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        pass
        # goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    p.run(timeout=50)
    if p.plan:
        print("ERROR!!!")
        for a in p.plan:
            print(a)
        raise Exception("Plan must be empty in this case")

def test_evict_and_killpod_deployment_without_service():
    "Test that killPod works for deployment"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    # create Deploymnent that we're going to detect failure of...
    d = Deployment()
    d.spec_replicas = 2

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,d,None)
    pod_running_2 = build_running_pod_with_d(2,2,2,n,d,None)

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    # pod_running_1.targetService = s
    # pod_running_1.hasService = True
    # pod_running_2.targetService = s
    pod_running_2.hasService = True

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, s, pod_pending_1, d])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_running_1.status == STATUS_POD["Pending"]
    p = NewGOal(k.state_objects)
    # print_objects(k.state_objects)
    p.run(timeout=150)
    assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_defined" in "\n".join([repr(x) for x in p.plan])
    assert "KillPod_IF_Deployment_isNotNUll_Service_isNull_Daemonset_isNull" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
    #     print(a) 

def test_evict_and_killpod_without_deployment_without_service():
    "Test that killPod works without either deployment or service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    # create Deploymnent that we're going to detect failure of...
    # d = Deployment()
    # d.spec_replicas = 2

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,None,None)
    pod_running_2 = build_running_pod_with_d(2,2,2,n,None,None)

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    # s.amountOfActivePods = 2
    # s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    # pod_running_1.targetService = s
    # pod_running_1.hasService = True
    # pod_running_2.targetService = s
    # pod_running_2.hasService = True

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, s, pod_pending_1])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_running_1.status == STATUS_POD["Pending"]
    p = NewGOal(k.state_objects)
    # print_objects(k.state_objects)
    p.run(timeout=150)
    # for a in p.plan:
    #     print(a) 
    assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_defined" in "\n".join([repr(x) for x in p.plan])
    assert "KillPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNull" in "\n".join([repr(x) for x in p.plan])


def test_evict_and_killpod_with_deployment_and_service():
    "Test that killPod works for deployment with service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    # create Deploymnent that we're going to detect failure of...
    d = Deployment()
    d.spec_replicas = 2

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,d,None)
    pod_running_2 = build_running_pod_with_d(2,2,2,n,d,None)

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    pod_running_1.targetService = s
    pod_running_1.hasService = True
    pod_running_2.targetService = s
    pod_running_2.hasService = True

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, s, pod_pending_1, d])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_running_1.status == STATUS_POD["Pending"]
    p = NewGOal(k.state_objects)
    # print_objects(k.state_objects)
    p.run(timeout=150)
    assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_defined" in "\n".join([repr(x) for x in p.plan])
    assert "KillPod_IF_Deployment_isNotNUll_Service_isNotNull_Daemonset_isNull" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
    #     print(a) 

def test_evict_and_killpod_with_daemonset_without_service():
    "Test that killPod works with daemonset"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    # create Deploymnent that we're going to detect failure of...
    ds = DaemonSet()

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,None,ds)
    pod_running_2 = build_running_pod_with_d(2,2,2,n,None,ds)


    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    # s.amountOfActivePods = 2
    # s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    # pod_running_1.targetService = s
    # pod_running_1.hasService = True
    # pod_running_2.targetService = s
    # pod_running_2.hasService = True

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, s, pod_pending_1,ds])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_running_1.status == STATUS_POD["Pending"]
    p = NewGOal(k.state_objects)
    # print_objects(k.state_objects)
    p.run(timeout=150)
    assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_defined" in "\n".join([repr(x) for x in p.plan])
    assert "KillPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
    #     print(a) 

def test_evict_and_killpod_with_daemonset_with_service():
    "Test that killPod works with daemonset and service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    # create Deploymnent that we're going to detect failure of...
    ds = DaemonSet()

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,None,ds)
    pod_running_2 = build_running_pod_with_d(2,2,2,n,None,ds)

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    pod_running_1.targetService = s
    pod_running_1.hasService = True
    pod_running_2.targetService = s
    pod_running_2.hasService = True

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, s, pod_pending_1,ds])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_running_1.status == STATUS_POD["Pending"]
    p = NewGOal(k.state_objects)
    # print_objects(k.state_objects)
    p.run(timeout=150)
    assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_defined" in "\n".join([repr(x) for x in p.plan])
    assert "KillPod_IF_Deployment_isNUll_Service_isNotNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
    #     print(a) 


def test_startpod_without_deployment_without_service():
    "Test that StartPod works without daemonset/deployment and service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
 
    ds = DaemonSet()

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,None,ds)

    # Service  
    s = Service()
    # s.metadata_name = "test-service"
    # s.amountOfActivePods = 2
    # s.status = STATUS_SERV["Started"]

 
    pod_running_1.targetService = s
    pod_running_1.hasService = True


    # Pending pod
    pod_pending_1 = build_pending_pod_with_d(3,2,2,n,None,None)

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pod_running_1, s, pod_pending_1,ds])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    # print_objects(k.state_objects)
    p.run(timeout=150)
    assert "SelectNode" in "\n".join([repr(x) for x in p.plan])
    assert "StartPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNull" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
        # print(a) 

def test_startpod_without_deployment_with_service():
    "Test that StartPod works without daemonset/deployment but with service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
 
    ds = DaemonSet()

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,None,ds)
    # Pending pod
    pod_pending_1 = build_pending_pod_with_d(3,2,2,n,None,None)
    
    # Service  
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 0
    s.status = STATUS_SERV["Pending"]
 
    pod_pending_1.targetService = s
    pod_pending_1.hasService = True

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pod_running_1, s, pod_pending_1,ds])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    # print_objects(k.state_objects)
    p.run(timeout=150)
    assert "SelectNode" in "\n".join([repr(x) for x in p.plan])
    assert "StartPod_IF_Deployment_isNUll_Service_isNotNull_Daemonset_isNull" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
        # print(a) 


def test_startpod_with_deployment_with_service():
    "Test that StartPod works with deployment and service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
 
    d = Deployment()
    d.spec_replicas = 2

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,d,None)
    # Pending pod
    pod_pending_1 = build_pending_pod_with_d(3,2,2,n,d,None)
    
    # Service  
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 0
    s.status = STATUS_SERV["Pending"]
 
    pod_running_1.targetService = s
    pod_running_1.hasService = True
    pod_pending_1.targetService = s
    pod_pending_1.hasService = True

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pod_running_1, s, pod_pending_1,d])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    # print_objects(k.state_objects)
    p.run(timeout=150)
    assert "SelectNode" in "\n".join([repr(x) for x in p.plan])
    assert "StartPod_IF_Deployment_isNotNUll_Service_isNotNull_Daemonset_isNull" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
        # print(a)



def test_startpod_with_daemonset_without_service():
    "Test that StartPod works with daemonset and without service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
 
    d = DaemonSet()

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,None,d)
    # Pending pod
    pod_pending_1 = build_pending_pod_with_d(3,2,2,n,None,d)
    
    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pod_running_1, pod_pending_1,d])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    print_objects(k.state_objects)
    p.run(timeout=150)
    for a in p.plan:
        print(a) 
    # assert "SelectNode" in "\n".join([repr(x) for x in p.plan])
    assert "StartPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])


def test_startpod_with_daemonset_with_service():
    "Test that StartPod works with daemonset and service"
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5
 
    d = DaemonSet()

    # Create running pods
    pod_running_1 = build_running_pod_with_d(1,2,2,n,None,d)
    # Pending pod
    pod_pending_1 = build_pending_pod_with_d(3,2,2,n,None,d)
    
    # Service  
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 0
    s.status = STATUS_SERV["Pending"]
 
    pod_running_1.targetService = s
    pod_running_1.hasService = True
    pod_pending_1.targetService = s
    pod_pending_1.hasService = True

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n, pod_running_1, s, pod_pending_1,d])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    print_objects(k.state_objects)
    p.run(timeout=150)
    for a in p.plan:
        print(a) 
    assert "StartPod_IF_Deployment_isNUll_Service_isNotNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])

def test_has_deployment_creates_daemonset__pods_evicted_pods_pending_synthetic():
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    # Create running pods
    pod_running_1 = build_running_pod(1,2,2,n)
    pod_running_2 = build_running_pod(2,2,2,n)

    ## Set consumptoin as expected
    n.currentFormalCpuConsumption = 4
    n.currentFormalMemConsumption = 4

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    # pod_running_1.targetService = s
    # pod_running_2.targetService = s

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    # create Deploymnent that we're going to detect failure of...
    d = Deployment()
    d.podList.add(pod_running_1)
    d.podList.add(pod_running_2)
    d.amountOfActivePods = 2
    d.spec_replicas = 2

    k.state_objects.extend([n, pc, pod_running_1, pod_running_2, pod_pending_1, d])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        pass
        # goal = lambda self: pod_pending_1.status == STATUS_POD["Running"]
    p = NewGOal(k.state_objects)
    p.run(timeout=50)
    assert "StartPod" in "\n".join([repr(x) for x in p.plan])
    assert "Evict" in "\n".join([repr(x) for x in p.plan])
    assert "MarkDeploymentOutageEvent" in "\n".join([repr(x) for x in p.plan])
    # for a in p.plan:
        # print(a) 

def test_creates_deployment_but_insufficient_resource__pods_pending_synthetic():
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    # Create running pods
    pod_running_1 = build_running_pod(1,2,2,n)
    pod_running_2 = build_running_pod(2,2,2,n)

    ## Set consumptoin as expected
    n.currentFormalCpuConsumption = 4
    n.currentFormalMemConsumption = 4

    # priority for pod-to-evict
    # pc = PriorityClass()
    # pc.priority = 10
    # pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    # pod_running_1.targetService = s
    # pod_running_2.targetService = s

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    # pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    # create Deploymnent that we're going to detect failure of...
    d = Deployment()
    d.podList.add(pod_running_1)
    d.podList.add(pod_running_2)
    d.amountOfActivePods = 2
    d.spec_replicas = 2

    dnew = Deployment()
    dnew.podList.add(pod_pending_1)
    dnew.amountOfActivePods = 0
    dnew.spec_replicas = 1

    k.state_objects.extend([n, pod_running_1, pod_running_2, pod_pending_1, d, dnew])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        pass
    p = NewGOal(k.state_objects)
    p.run(timeout=50)
    # for a in p.plan:
        # print(a) 
    assert "MarkDeploymentOutageEvent" in "\n".join([repr(x) for x in p.plan])


def test_creates_service_and_deployment_insufficient_resource__service_outage():
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    globalVar = next(filter(lambda x: isinstance(x, GlobalVar), k.state_objects))
    # initial node state
    n = Node()
    n.cpuCapacity = 5
    n.memCapacity = 5

    # Create running pods
    pod_running_1 = build_running_pod(1,2,2,n)
    pod_running_2 = build_running_pod(2,2,2,n)

    ## Set consumptoin as expected
    n.currentFormalCpuConsumption = 4
    n.currentFormalMemConsumption = 4

    # priority for pod-to-evict
    # pc = PriorityClass()
    # pc.priority = 10
    # pc.metadata_name = "high-prio-test"

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    pod_running_1.targetService = s
    pod_running_2.targetService = s

    # Pending pod
    pod_pending_1 = build_pending_pod(3,2,2,n)
    # pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    # create Deploymnent that we're going to detect failure of...
    d = Deployment()
    d.podList.add(pod_running_1)
    d.podList.add(pod_running_2)
    d.amountOfActivePods = 2
    d.spec_replicas = 2

    dnew = Deployment()
    dnew.podList.add(pod_pending_1)
    dnew.amountOfActivePods = 0
    dnew.spec_replicas = 1

    snew = Service()
    snew.metadata_name = "test-service-new"
    snew.amountOfActivePods = 0
    # snew.status = STATUS_SERV["Started"]
    pod_pending_1.targetService = snew

    k.state_objects.extend([n, s, snew, pod_running_1, pod_running_2, pod_pending_1, d, dnew])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        goal = lambda self: globalVar.is_service_disrupted == True and \
                scheduler.status == STATUS_SCHED["Clean"]
    p = NewGOal(k.state_objects)
    p.run(timeout=50)
    # for a in p.plan:
        # print(a)
    assert "MarkServiceOutageEvent" in "\n".join([repr(x) for x in p.plan])

# Simple test for pod 
def test_synthetic_start_pod_with_scheduler():
    k = KubernetesCluster()
    pods = []
    node = Node()
    node.memCapacity = 3
    node.cpuCapacity = 3
    for i in range(2):
        pod = Pod()
        pod.metadata_name = "pod_number_" + str(i)
        pod.memRequest = 1
        pod.cpuRequest = 1
        pods.append(pod)
    pods[0].status = STATUS_POD["Running"]
    pods[0].atNode = node

    # pods[1].toNode = node


    k.state_objects.extend(pods)
    k.state_objects.append(node)

    # k._build_state() # TODO may be should uncomments
    
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    scheduler.status = STATUS_SCHED["Changed"]
    scheduler.podQueue.add(pods[1])
    scheduler.queueLength += 1
    class TestRun(K8ServiceInterruptSearch):
        goal = lambda self: pods[1].status == STATUS_POD["Running"]
    p = TestRun(k.state_objects)
    p.xrun()
    print_objects(k.state_objects)
    # print(p.plan)
    for pod in filter(lambda x: isinstance(x, Pod), k.state_objects):
        # this one test broken
        assert pod.status == STATUS_POD["Running"], "All pods should be Running in this case. Some pod is {0}".format(pod.status._get_value())
        # use 
        assert pod.status._get_value() == "Running", "All pods should be Running in this case. Some pod is {0}".format(pod.status._get_value())


def test_has_deployment_creates_deployment__pods_evicted_pods_pending():
    k = KubernetesCluster()
    prios = {}
    pch = PriorityClass()
    k.state_objects.append(pch)
    pch.priority = 10
    pch.metadata_name = "high-prio-test"
    prios["high"] = pch
    pcl = PriorityClass()
    k.state_objects.append(pcl)
    pcl.priority = 1
    pcl.metadata_name = "low-prio-test"
    prios["low"] = pcl

    pods = []
    node = Node()
    k.state_objects.append(node)
    node.memCapacity = 3
    node.cpuCapacity = 3
    d_was = Deployment()
    k.state_objects.append(d_was)
    d_was.metadata_name = "d_was"
    d_was.priorityClass = prios["low"]
    d_was.spec_template_spec_priorityClassName = prios["low"].metadata_name
    d_was.amountOfActivePods = 2
    d_was.spec_replicas = 2
    for i in range(2):
        pod = Pod()
        k.state_objects.append(pod)
        pod.metadata_name = "pod_number_" + str(i)
        pod.memRequest = 1
        pod.cpuRequest = 1
        pod.status = STATUS_POD["Running"]
        pod.priorityClass = prios["low"]
        pod.spec_priorityClassName = prios["low"].metadata_name
        pod.hasDeployment = True
        pods.append(pod)
        node.amountOfActivePods += 1
        node.currentFormalMemConsumption += pod.memRequest
        node.currentFormalCpuConsumption += pod.cpuRequest
        d_was.podList.add(pod)

    d_new = Deployment()
    d_new.metadata_name = "d_new"
    d_new.spec_replicas = 2
    d_new.priorityClass = prios["high"]
    d_new.spec_template_spec_priorityClassName = prios["high"].metadata_name
    d_new.memRequest = 1
    d_new.cpuRequest = 1
    d_new.hook_after_create(k.state_objects)
    k.state_objects.append(d_new)


    pod_pending_count = 0
    pPod = []
    for pod in filter(lambda x: isinstance(x, Pod), k.state_objects):
        if "pod_number_" in pod.metadata_name._get_value():
            assert pod.status._get_value() == "Running", "pod_number_X pods should be Running before planning but have {0} status".format(pod.status._get_value())
        if pod.status._get_value() == "Pending":
            pod_pending_count += 1
            pPod.append(pod)
    assert pod_pending_count == 2, "should be 2 pod in pending have only {0}".format(pod_pending_count)

    class TestRun(K8ServiceInterruptSearch):
        goal = lambda self: self.scheduler.status == STATUS_SCHED["Clean"] and pPod[0].status == STATUS_POD["Running"]and pPod[1].status == STATUS_POD["Running"]

    p = TestRun(k.state_objects)
    # print_objects(k.state_objects)
    # p.run()
    # print("scenario \n{0}".format(p.plan))
    p.xrun()
    # print("---after calculation ----")
    # print_objects(k.state_objects)

    assert d_new.amountOfActivePods == 2
    assert d_was.amountOfActivePods == 1
    assert node.amountOfActivePods == 3

    for pod in filter(lambda x: isinstance(x, Pod), k.state_objects):
        if "d_new" in pod.metadata_name._get_value():
            assert pod.status._get_value() == "Running", "{1} pods should be Running after planning but have {0} status".format(pod.status._get_value(),pod.metadata_name._get_value() )

@pytest.mark.skip(reason="This test case is broken see #109")
def test_scheduller_counter_bug():
    k = KubernetesCluster()
    prios = {}
    pch = PriorityClass()
    k.state_objects.append(pch)
    pch.priority = 10
    pch.metadata_name = "high-prio-test"
    prios["high"] = pch
    pcl = PriorityClass()
    k.state_objects.append(pcl)
    pcl.priority = 1
    pcl.metadata_name = "low-prio-test"
    prios["low"] = pcl

    pods = []
    node = Node()
    k.state_objects.append(node)
    node.memCapacity = 3
    node.cpuCapacity = 3
    d_was = Deployment()
    k.state_objects.append(d_was)
    d_was.metadata_name = "d_was"
    d_was.priorityClass = prios["low"]
    d_was.spec_template_spec_priorityClassName = prios["low"].metadata_name
    d_was.amountOfActivePods = 2
    d_was.spec_replicas = 2
    for i in range(2):
        pod = Pod()
        k.state_objects.append(pod)
        pod.metadata_name = "pod_number_" + str(i)
        pod.memRequest = 1
        pod.cpuRequest = 1
        pod.status = STATUS_POD["Running"]
        pod.priorityClass = prios["low"]
        pod.spec_priorityClassName = prios["low"].metadata_name
        pod.hasDeployment = True
        pods.append(pod)
        node.amountOfActivePods += 1
        node.currentFormalMemConsumption += pod.memRequest
        node.currentFormalCpuConsumption += pod.cpuRequest
        d_was.podList.add(pod)

    d_new = Deployment()
    d_new.metadata_name = "d_new"
    d_new.spec_replicas = 2
    d_new.priorityClass = prios["high"]
    d_new.spec_template_spec_priorityClassName = prios["high"].metadata_name
    d_new.memRequest = 1
    d_new.cpuRequest = 1
    d_new.hook_after_create(k.state_objects)
    k.state_objects.append(d_new)

    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    pPod = []

    for pod in filter(lambda x: isinstance(x, Pod), k.state_objects):
        if pod.status._get_value() == "Pending":
            pPod.append(pod)

    class TestRun(K8ServiceInterruptSearch):
        goal = lambda self: self.scheduler.status == STATUS_SCHED["Clean"] and pPod[0].status == STATUS_POD["Running"]and pPod[1].status == STATUS_POD["Running"]

    p = TestRun(k.state_objects)
    p.xrun()
    assert scheduler.queueLength._get_value() == 0
    assert len(scheduler.podQueue._get_value()) == 0

def test_1154_has_daemonset_creates_deployment__pods_evicted_daemonset_outage_synthetic():
    # Initialize scheduler, globalvar
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    globalvar = next(filter(lambda x: isinstance(x, GlobalVar), k.state_objects))
    # initial node state
    n1 = Node("node 1")
    n1.cpuCapacity = 3
    n1.memCapacity = 3

    n2 = Node("node 2")
    n2.cpuCapacity = 3
    n2.memCapacity = 3


    #Create Daemonset
    ds = DaemonSet()
    ds.searchable = True

    # Create running pods as Daemonset
    pod_running_1 = build_running_pod_with_d(1,2,2,n1,None,ds)
    pod_running_2 = build_running_pod_with_d(2,2,2,n2,None,ds)

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    # s.amountOfActivePods = 2
    # s.status = STATUS_SERV["Started"]
    # pod_running_1.targetService = s
    # pod_running_2.targetService = s

    # Pending pod with deployment
    d = Deployment()
    d.spec_replicas = 1
    d.priorityClass = pc

    pod_pending_1 = build_pending_pod_with_d(3,2,2,n1,d,None)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n1, n2, pc, pod_running_1, pod_running_2, pod_pending_1, d,ds])
    print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        # pass
        goal = lambda self: globalvar.is_daemonset_disrupted == True
    p = NewGOal(k.state_objects)
    p.run(timeout=50)
    print("---after calculation ----")
    print_objects(k.state_objects)
    for a in p.plan:
        print(a) 
    # assert "StartPod" in "\n".join([repr(x) for x in p.plan])
    # assert "Evict" in "\n".join([repr(x) for x in p.plan])
    # assert "MarkDeploymentOutageEvent" in "\n".join([repr(x) for x in p.plan])


def construct_space_2119_has_daemonset_with_service_creates_deployment__pods_evicted_daemonset_outage_synthetic():
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    globalvar = next(filter(lambda x: isinstance(x, GlobalVar), k.state_objects))
    # initial node state
    n1 = Node()
    n1.metadata_name = "node 1"
    n1.cpuCapacity = 3
    n1.memCapacity = 3
    n1.isNull == False

    n2 = Node("node 2")
    n2.metadata_name = "node 2"
    n2.cpuCapacity = 3
    n2.memCapacity = 3
    n2.isNull == False


    #Create Daemonset
    ds = DaemonSet()
    ds.searchable = True

    # Create running pods as Daemonset
    pod_running_1 = build_running_pod_with_d(1,2,2,n1,None,ds)
    pod_running_2 = build_running_pod_with_d(2,2,2,n2,None,ds)

    # priority for pod-to-evict
    pc = PriorityClass()
    pc.priority = 10
    pc.metadata_name = "high-prio-test"

    # # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]
    pod_running_1.targetService = s
    pod_running_2.targetService = s

    # Pending pod with deployment
    d = Deployment()
    d.spec_replicas = 1
    d.priorityClass = pc

    pod_pending_1 = build_pending_pod_with_d(3,2,2,n1,None,None)
    pod_pending_1.priorityClass = pc # high prio will evict!

    ## Add pod to scheduler queue
    scheduler.podQueue.add(pod_pending_1)
    scheduler.queueLength += 1
    scheduler.status = STATUS_SCHED["Changed"]

    k.state_objects.extend([n1,  pc, pod_running_1, pod_running_2, pod_pending_1, d, ds])
    return k,pod_running_1

def test_1218_has_daemonset_with_service_creates_deployment__pods_evicted_daemonset_outage_synthetic_step1():
    # Initialize scheduler, globalvar
    k,pod_running_1=construct_space_2119_has_daemonset_with_service_creates_deployment__pods_evicted_daemonset_outage_synthetic()
    class NewGOal(AnyGoal):
        # pass
        # goal = lambda self: globalvar.is_daemonset_disrupted == True
        goal = lambda self: pod_running_1.status == STATUS_POD["Killing"]
    p = NewGOal(k.state_objects)
    p.run(timeout=400)
    # for a in p.plan:
    #     print(a) 
    assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_not_defined" in "\n".join([repr(x) for x in p.plan])
    # assert "MarkDeploymentOutageEvent" in "\n".join([repr(x) for x in p.plan])

def test_1292_has_daemonset_with_service_creates_deployment__pods_evicted_daemonset_outage_synthetic_step2():
    # Initialize scheduler, globalvar
    k,pod_running_1=construct_space_2119_has_daemonset_with_service_creates_deployment__pods_evicted_daemonset_outage_synthetic()
    print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        # pass
        # goal = lambda self: globalvar.is_daemonset_disrupted == True
        goal = lambda self: pod_running_1.status == STATUS_POD["Pending"]
    p = NewGOal(k.state_objects)
    p.run(timeout=400)
    print("---after calculation ----")
    print_objects(k.state_objects)
    for a in p.plan:
        print(a) 
    assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_not_defined" in "\n".join([repr(x) for x in p.plan])
    assert "KillPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
  
def test_1310_has_daemonset_with_service_creates_deployment__pods_evicted_daemonset_outage_synthetic_step3():
    # Initialize scheduler, globalvar
    k,pod_running_1=construct_space_2119_has_daemonset_with_service_creates_deployment__pods_evicted_daemonset_outage_synthetic()
    globalvar = next(filter(lambda x: isinstance(x, GlobalVar), k.state_objects))
    class NewGOal(AnyGoal):
        # pass
        goal = lambda self: globalvar.is_daemonset_disrupted == True
    p = NewGOal(k.state_objects)
    p.run(timeout=400)
    # print_objects(k.state_objects)
    # for a in p.plan:
    #     print(a) 
    assert "StartPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_not_defined" in "\n".join([repr(x) for x in p.plan])
    assert "KillPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    assert "MarkDaemonsetOutageEvent" in "\n".join([repr(x) for x in p.plan])

def construct_space_1322_has_service_only_on_node_that_gets_disrupted():
    k = KubernetesCluster()
    scheduler = next(filter(lambda x: isinstance(x, Scheduler), k.state_objects))
    globalvar = next(filter(lambda x: isinstance(x, GlobalVar), k.state_objects))
    # initial node state
    n1 = Node()
    n1.metadata_name = "node 1"
    n1.cpuCapacity = 6
    n1.memCapacity = 6
    n1.isNull == False

    n2 = Node("node 2")
    n2.metadata_name = "node 2"
    n2.cpuCapacity = 6
    n2.memCapacity = 6
    n2.isNull == False

    # Create running pods as Daemonset
    pod_running_1 = build_running_pod_with_d(1,2,2,n1,None,None)
    pod_running_2 = build_running_pod_with_d(2,2,2,n1,None,None)
    pod_running_3 = build_running_pod_with_d(3,2,2,n1,None,None)
    pod_running_4 = build_running_pod_with_d(4,2,2,n2,None,None)
    pod_running_5 = build_running_pod_with_d(5,2,2,n2,None,None)
    pod_running_6 = build_running_pod_with_d(6,2,2,n2,None,None)

    # # Service to detecte eviction
    s1 = Service()
    s1.metadata_name = "test-service1"
    s1.amountOfActivePods = 2
    s1.status = STATUS_SERV["Started"]
    
    s2 = Service()
    s2.metadata_name = "test-service2"
    s2.amountOfActivePods = 4
    s2.status = STATUS_SERV["Started"]

    pod_running_1.targetService = s1
    pod_running_2.targetService = s1
    pod_running_3.targetService = s2
    pod_running_4.targetService = s2
    pod_running_5.targetService = s2
    pod_running_6.targetService = s2

    pod_running_1.hasService = True
    pod_running_2.hasService = True
    pod_running_3.hasService = True
    pod_running_4.hasService = True
    pod_running_5.hasService = True
    pod_running_6.hasService = True

    ## We have clean scheduler queue
    scheduler.status = STATUS_SCHED["Clean"]

    k.state_objects.extend([n1,  n2, s1, s2, pod_running_1, pod_running_2, pod_running_3, pod_running_4, pod_running_5, pod_running_6])
    return k,n1

def test_1372_node_outage_with_service_eviction_step1():
    # Initialize scheduler, globalvar
    k,n1=construct_space_1322_has_service_only_on_node_that_gets_disrupted()
    globalvar = next(filter(lambda x: isinstance(x, GlobalVar), k.state_objects))
    class NewGOal(AnyGoal):
        goal = lambda self: n1.status == STATUS_NODE["Inactive"]
    p = NewGOal(k.state_objects)
    p.run(timeout=400)
    print_objects(k.state_objects)
    for a in p.plan:
        print(a) 
    assert "Initiate_node_outage" in "\n".join([repr(x) for x in p.plan])
    # assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_not_defined" in "\n".join([repr(x) for x in p.plan])
    # assert "KillPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    # assert "MarkDaemonsetOutageEvent" in "\n".join([repr(x) for x in p.plan])
    
    
def test_1395_node_outage_with_service_eviction_step2():
    # Initialize scheduler, globalvar
    k,n1=construct_space_1322_has_service_only_on_node_that_gets_disrupted()
    globalvar = next(filter(lambda x: isinstance(x, GlobalVar), k.state_objects))
    class NewGOal(AnyGoal):
        goal = lambda self: globalvar.is_node_disrupted == True
    p = NewGOal(k.state_objects)
    p.run(timeout=400)
    print_objects(k.state_objects)
    for a in p.plan:
        print(a) 
    # assert "StartPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    # assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_not_defined" in "\n".join([repr(x) for x in p.plan])
    # assert "KillPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    # assert "MarkDaemonsetOutageEvent" in "\n".join([repr(x) for x in p.plan])

def test_1411_node_outage_with_service_eviction_step3():
    # Initialize scheduler, globalvar
    k,n1=construct_space_1322_has_service_only_on_node_that_gets_disrupted()
    globalvar = next(filter(lambda x: isinstance(x, GlobalVar), k.state_objects))
    class NewGOal(AnyGoal):
        goal = lambda self: globalvar.is_node_disrupted == True and globalvar.is_service_disrupted == True
    p = NewGOal(k.state_objects)
    p.run(timeout=1000)
    print_objects(k.state_objects)
    for a in p.plan:
        print(a) 
    # assert "StartPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    # assert "Evict_and_replace_less_prioritized_pod_when_target_node_is_not_defined" in "\n".join([repr(x) for x in p.plan])
    # assert "KillPod_IF_Deployment_isNUll_Service_isNull_Daemonset_isNotNull" in "\n".join([repr(x) for x in p.plan])
    # assert "MarkDaemonsetOutageEvent" in "\n".join([repr(x) for x in p.plan])