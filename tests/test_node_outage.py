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


def test_single_node_outage():
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

    # Service to detecte eviction
    s = Service()
    s.metadata_name = "test-service"
    s.amountOfActivePods = 2
    s.status = STATUS_SERV["Started"]

    # our service has multiple pods but we are detecting pods pending issue
    # remove service as we are detecting service outage by a bug above
    pod_running_1.targetService = s
    pod_running_2.targetService = s
    pod_running_1.hasService = True
    pod_running_2.hasService = True

    # create Deploymnent that we're going to detect failure of...
    d = Deployment()
    d.podList.add(pod_running_1)
    d.podList.add(pod_running_2)
    d.amountOfActivePods = 2
    d.spec_replicas = 2
    pod_running_1.hasDeployment = True
    pod_running_2.hasDeployment = True

    k.state_objects.extend([n, s, pod_running_1, pod_running_2, d])
    # print_objects(k.state_objects)
    class NewGOal(AnyGoal):
        # goal = lambda self: globalVar.is_service_disrupted == True and \
                # scheduler.status == STATUS_SCHED["Clean"]
        goal = lambda self: globalVar.is_node_disrupted == True and globalVar.is_service_disrupted == True
    p = NewGOal(k.state_objects)
    p.run(timeout=70)
    for a in p.plan:
        print(a) 
    assert "MarkServiceOutageEvent" in "\n".join([repr(x) for x in p.plan])

