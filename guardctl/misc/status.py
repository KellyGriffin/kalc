from guardctl.model.action.default_limits import *
from guardctl.model.action.eviction import *
from guardctl.model.action.oom_kill import *
from guardctl.model.action.scheduler import *
import poodle.problem

class ProblemTemplate(poodle.problem.Problem):
    constSymbol = {}
    pod = []
    node = []
    kubeProxy = []
    loadbalancer = []
    service = []
    daemonSet = []
    request = []
    containerConfig = []
    priorityDict = {}

    def constFactory(self, statusNameList, objType):
        for statusName in statusNameList:
            self.constSymbol[statusName] = self.addObject(objType(statusName))

    def problem(self):
                STATUS_REQ_ATSTART = Status()
                STATUS_REQ_ATLOADBALANCER = Status()
                STATUS_REQ_ATKUBEPROXY = Status()
                STATUS_REQ_ATPODINPUT = Status()
                STATUS_REQ_MEMRESOURCECONSUMED = Status()
                STATUS_REQ_CPURESOURCECONSUMED = Status()
                STATUS_REQ_RESOURCESCONSUMED = Status()
                STATUS_REQ_DIRECTEDTOPOD = Status()
                STATUS_REQ_REQUESTPIDTOBEENDED = Status()
                STATUS_REQ_CPURESOURCERELEASED = Status()
                STATUS_REQ_MEMRESOURCERELEASED = Status()
                STATUS_REQ_RESOURCESRELEASED = Status()
                STATUS_REQ_REQUESTTERMINATED = Status()
                STATUS_REQ_REQUESTFINISHED = Status()
                STATUS_POD_ATCONFIG = Status()
                STATUS_POD_READYTOSTART = Status()
                STATUS_POD_ACTIVE = Status()
                STATUS_POD_PENDING = Status()
                STATUS_POD_ATMANUALCREATION = Status()
                STATUS_POD_DIRECTEDTONODE = Status()
                STATUS_POD_CPUCONSUMED = Status()
                STATUS_POD_RESOURCEFORMALCONSUMPTIONFAILED = Status()
                STATUS_POD_FAILEDTOSTART = Status()
                STATUS_POD_READYTOSTART2 = Status()
                STATUS_POD_MEMCONSUMED = Status()
                STATUS_POD_MEMCONSUMEDFAILED = Status()
                STATUS_POD_BINDEDTONODE = Status()
                STATUS_POD_RUNNING = Status()
                STATUS_POD_SUCCEEDED = Status() # MAY BE LOST BE CAREFUL
                STATUS_POD_KILLING = Status()
                STATUS_POD_FAILED = Status()
                STATUS_NODE_RUNNING = Status()
                STATUS_NODE_SUCCEDED = Status()
                STATUS_POD_PENDING = Status()
                STATUS_NODE_DELETED = Status()
                STATUS_POD_INACTIVE = Status()
                STATUS_NODE_ACTIVE = Status()
                STATUS_NODE_INACTIVE = Status()
                STATUS_REQ_DIRECTEDTONODE = Status()
                STATUS_REQ_NODECAPACITYOVERWHELMED = Status()
                STATUS_LIM_MET = Status()
                STATUS_LIM_OVERWHELMED = Status()
                TEST = Status()
                STATUS_POD_TOBETERMINATED = Status()
                STATUS_POD_TERMINATED = Status()
                STATUS_SERV_PENDING = Status()
                STATUS_SERV_STARTED = Status()
                STATUS_SERV_INTERRUPTED = Status()
                STATUS_REQ_RUNNING = Status()
                STATUS_POD_INITIALCONRELEASED = Status()
                STATUS_POD_GLOBALMEMCONSUMED = Status()
                STATUS_POD_GLOBALCPUCONSUMED = Status()
                STATUS_POD_FORMALCONRELEASED = Status()
                STATUS_SCHED_CLEAN = Status()
                STATUS_SCHED_CHANGED = Status()
                STATUS_POD_READYTOSTART = Status()
                STATUS_POD_FINISHEDPLACEMENT = Status()
        
                STATE_POD_SUCCEEDED = State()
                STATE_POD_RUNNING = State()
                STATE_POD_PENDING = State()
                STATE_POD_ACTIVE = State()
                STATE_POD_INACTIVE = State()
                STATE_REQ_STARTED = State()
                STATE_REQUEST_ACTIVE = State()
                STATE_REQUEST_INACTIVE = State()
                STATE_NODE_ACTIVE = State()
                STATE_NODE_INACTIVE = State()
                NULL = Type()

    def problem(self):	        

        pass