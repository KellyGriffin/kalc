import subprocess
import json
from poodle import Object
from kalc.model.full import kinds_collection
from kalc.misc.kind_filter import FilterByLabelKey, FilterByName, KindPlaceholder
from kalc.model.kubernetes import KubernetesCluster
import kalc.policy 
from kalc.model.search import KubernetesModel
from kalc.model.kinds.Deployment import YAMLable, Deployment
import random

kalc_state_objects = []
kind = KindPlaceholder

kalc.policy.policy_engine.register_state_objects(kalc_state_objects)

for k, v in kinds_collection.items():
    v.by_name = FilterByName(k, kalc_state_objects)
    v.by_label = FilterByLabelKey(k, kalc_state_objects)
    globals()[k] = v
    setattr(kind, k, v)

def update():
    "Fetch information from currently selected ccluster"
    result = subprocess.run(['kubectl', 'get', 'all', '-o=json'], stdout=subprocess.PIPE)
    if len(result.stdout) < 100:
        raise SystemError("Error using kubectl. Make sure `kubectl get pods` is working.")
    data = json.loads(result.stdout.decode("utf-8"))
    k = KubernetesCluster()
    for item in data["items"]:
        k.load_item(item)
    k._build_state()
    global kalc_state_objects
    kalc_state_objects.clear()
    kalc_state_objects.extend(k.state_objects)

def run():
    kube = KubernetesModel(kalc_state_objects)
    for ob in kalc_state_objects:
        if isinstance(ob.policy, str): continue # STUB. find and fix
        for pname, pobject in ob.policy._instantiated_policies.items():
            if pobject.activated:
                for hname, hval in pobject.hypotheses.items():
                    # print("Adding hypothesis goal")
                    pobject.clear_goal()
                    hval()
                    kube.add_goal_eq(pobject.get_goal_eq())
                    kube.add_goal_in(pobject.get_goal_in())
                for name in dir(pobject):
                    if callable(getattr(pobject, name)) and hasattr(getattr(pobject, name), "_planned"):
                        # print("Adding method from policy")
                        setattr(kube, name, getattr(pobject, name))
    kube.run(timeout=1000, sessionName="kalc")
    # TODO. STUB
    # TODO example hanlers and patches
    for obj in kalc_state_objects:
        if isinstance(obj, Deployment):
            obj.affinity_required_handler()
            obj.scale_replicas_hook(random.randint(2,10))
    patch()
    # for a in kube.plan:
    #     print(a)
    #     r = a()
    #     if isinstance(r, dict) and "kubectl" in r:
    #         print(">>", r["kubectl"])
    # print summary

def patch():
    for obj in k.state_objects:
        if isinstance(obj, YAMLable):
            print(obj.metadata_name)
            print(obj.get_patch())

def apply():
    pass