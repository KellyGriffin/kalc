from poodle import schedule
from poodle.schedule import SchedulingError

class ProblemTemplate:
    def __init__(self, objectList=[]):
        self.plan = None
        self.objectList = objectList
        self.pod = []
        self.node = []
        self.kubeProxy = []
        self.loadbalancer = []
        self.service = []
        self.controller = []
        self.request = []
        self.containerConfig = []
        self.priorityDict = {}
    
    def problem(self):
        pass

    def addObject(self, obj):
        self.objectList.append(obj)
        return obj

    # fill object with corresponding list (list instance in lower case)
    def fillObjectLists(self):
        requiredObject = ['Pod', "Node", "Service", "LoadBalancer", "DaemonSet", "Deployment"]
        for obj in self.objectList:
            if obj.__class__.__name__ in requiredObject:
                try:
                    getattr(self, obj.__class__.__name__.lower()).append(obj)
                except:
                    pass

    def run(self, timeout=30):
        self.problem()
        self_methods = [getattr(self,m) for m in dir(self) if callable(getattr(self,m))]
        model_methods = []
        methods_scanned = set()
        for obj in self.objectList:
            if not obj.__class__.__name__ in methods_scanned:
                methods_scanned.add(obj.__class__.__name__)
                for m in dir(obj):
                    if callable(getattr(obj, m)):
                        model_methods.append(getattr(obj, m))
        try:
            self.plan = schedule(
                methods=self_methods + list(model_methods), 
                space=list(self.__dict__.values())+self.objectList,
                goal=lambda:(self.goal()),
                timeout=timeout,
                sessionName=self.__class__.__name__
                #exit=self.exit
            )
        except SchedulingError:
            pass

    def goal(self):
        pass