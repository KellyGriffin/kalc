import pytest
import yaml
from kalc.model.kubernetes import KubernetesCluster
from kalc.model.kinds.Pod import Pod
from kalc.model.kinds.Node import Node
from kalc.model.kinds.Service import Service
from kalc.model.kinds.PriorityClass import PriorityClass
from kalc.misc.const import *
# from kalc.model.search import K8ServiceInterruptSearch, AnyDeploymentInterrupted
from kalc.model.search import Check_services 
from kalc.misc.object_factory import labelFactory
from poodle import debug_plan
from poodle.schedule import EmptyPlanError
from kalc.model.scenario import Scenario
import kalc.model.kinds.Service as mservice
from tests.test_util import print_objects

pytestmark = pytest.mark.skip # TODO DELETEME

TEST_CLUSTER_FOLDER = "./tests/dataset_small_1/cluster_dump"
TEST_DEPLOYMENT = "./tests/dataset_small_1/deployment.yaml"

EXCLUDED_SERV = {
    "redis-master" : TypeServ("redis-master"),
    "redis-master-evict" : TypeServ("redis-master-evict"),
    "default-http-backend" : TypeServ("default-http-backend"),
    "redis-slave" : TypeServ("redis-slave"),
    "heapster": TypeServ("heapster")
    # -d ./tests/daemonset_eviction_with_deployment/cluster_dump/ -f ./tests/daemonset_eviction_with_deployment/daemonset_create.yaml -e Service:redis-master,Service:redis-master-evict,Service:default-http-backend,Service:redis-slave
}

def mark_excluded_service(object_space):
    services = filter(lambda x: isinstance(x, mservice.Service), object_space)
    for service in services:
        if service.metadata_name in list(EXCLUDED_SERV):
           service.searchable = False

# class AnyDeploymentInterrupted(K8ServiceInterruptSearch):

#     goal = lambda self: self.globalVar.is_deployment_disrupted == True and \
#             self.scheduler.status == STATUS_SCHED["Clean"]
class OptimisticRun(Check_services):

    goal = lambda self: self.scheduler.status == STATUS_SCHED["Clean"]

ALL_STATE = None

import logzero
logzero.logfile("./test.log", disableStderrLogger=False)


def test_anydeployment_interrupted_fromfiles():
    k = KubernetesCluster()
    k.load_dir(TEST_CLUSTER_FOLDER)
    k.create_resource(open(TEST_DEPLOYMENT).read())
    k._build_state()
    mark_excluded_service(k.state_objects)
    print("------Objects before solver processing------")
    print_objects(k.state_objects)
    p = AnyDeploymentInterrupted(k.state_objects)
    p.run(timeout=6600, sessionName="test_anydeployment_interrupted_fromfiles")
    if not p.plan:
        raise Exception("Could not solve %s" % p.__class__.__name__)
    print("------Objects after solver processing------")
    print(Scenario(p.plan).asyaml())
    print_objects(k.state_objects)
