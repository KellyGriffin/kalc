import yaml
from guardctl.importers.problemConfigLoad import KubernetesYAMLLoad
from collections import defaultdict
from guardctl.model.object.k8s_classes import Service, Label, Pod, Service, Deployment
from guardctl.misc.object_factory import labelFactory
from poodle import planned
from guardctl.misc.util import dget

class KubernetesCluster:
    def __init__(self):
        self.dict_states = defaultdict(list)
        self.state_objects = []

    def load_state(self, conf: str):
        "Load kubernetes state from file"
        d = yaml.safe_load(conf)
        for item in d["items"]:
            self.dict_states[item["kind"]].append(item)
    
    def load_kind(self, kind):
        for item in self.dict_states[kind]: 
            self.state_objects.append(getattr(self, "load_%s" % kind.lower())(item))

    def build_state(self):
        "After loading all configs, we build the state space"
        CONTROLLERS = ["Service", "Deployment"]
        for kind in ["Node"] + CONTROLLERS + ["Pod"]:
            self.load_kind(kind)

    #########################################
    # Loading of different kinds
    #

    def load_pod(self, podk):
        kl = KubernetesYAMLLoad()
        return kl._loadPodFromDict(podk)
    
    def load_node(self, node):
        kl = KubernetesYAMLLoad()
        return kl._loadNodeFromDict(node)

    def load_service(self, service: dict):
        s = Service(service["name"])
        s.nameString = service["name"]
        for name, value in service["labels"].items():
            s.labels.add(labelFactory.get(name, value))
        return s
        
    def load_deployment(self, deployment: dict):
        name = dget(deployment, "metadata/name", "NO_NAME")
        d = Deployment(name)
        d.nameString = name
        return d

    #
    #########################################

    def create_resource(self, res: str):
        raise
    
    def fetch_default(self):
        raise
    