from poodle import Object
from guardctl.model.system.primitives import StatusServ, StatusNode, StatusPod, StatusLim, StatusSched, StatusReq, Type
from guardctl.misc.object_factory import stringFactory

# STATE_NODE_ACTIVE = State()
# STATE_NODE_INACTIVE = State()
# STATE_POD_ACTIVE = State()
# STATE_POD_INACTIVE = State()
# STATE_POD_PENDING = State()
# STATE_POD_RUNNING = State()
# STATE_POD_SUCCEEDED = State()
# STATE_REQ_STARTED = State()
# STATE_REQUEST_ACTIVE = State()
# STATE_REQUEST_INACTIVE = State()
# STATUS_LIM_MET = StatusLim()
# STATUS_LIM_EXCEEDED = StatusLim()
# STATUS_NODE_ACTIVE = StatusNode()
# STATUS_NODE_DELETED = StatusNode()
# STATUS_NODE_INACTIVE = StatusNode()
# STATUS_NODE_RUNNING = StatusNode()
# STATUS_NODE_SUCCEDED = StatusNode()
# STATUS_POD_FAILED = StatusPod()
# STATUS_POD_KILLING = StatusPod()
STATUS_POD_PENDING = stringFactory.get("Pending") 
STATUS_POD_RUNNING = stringFactory.get("Running")

# STATUS_POD_SUCCEEDED = StatusPod() # MAY BE LOST BE CAREFUL
# STATUS_POD_TERMINATED = StatusPod()
# STATUS_POD_TOBETERMINATED = StatusPod()
# STATUS_REQ_ATKUBEPROXY = StatusReq()
# STATUS_REQ_ATLOADBALANCER = StatusReq()
# STATUS_REQ_ATPODINPUT = StatusReq()
# STATUS_REQ_ATSTART = StatusReq()
# STATUS_REQ_CPURESOURCECONSUMED = StatusReq()
# STATUS_REQ_CPURESOURCERELEASED = StatusReq()
# STATUS_REQ_DIRECTEDTONODE = StatusReq()
# STATUS_REQ_DIRECTEDTOPOD = StatusReq()
# STATUS_REQ_MEMRESOURCECONSUMED = StatusReq()
# STATUS_REQ_MEMRESOURCERELEASED = StatusReq()
# STATUS_REQ_NODECAPACITYOVERWHELMED = StatusReq()
# STATUS_REQ_REQUESTFINISHED = StatusReq()
# STATUS_REQ_REQUESTPIDTOBEENDED = StatusReq()
# STATUS_REQ_REQUESTTERMINATED = StatusReq()
# STATUS_REQ_RESOURCESCONSUMED = StatusReq()
# STATUS_REQ_RESOURCESRELEASED = StatusReq()
# STATUS_REQ_RUNNING = StatusReq()
STATUS_SCHED_CHANGED =  stringFactory.get("Changed")
STATUS_SCHED_CLEAN   =  stringFactory.get("Clean")
STATUS_SERV_INTERRUPTED = stringFactory.get("Interrupted")
STATUS_SERV_PENDING = stringFactory.get("Pending")
# stringFactory.get("Started") = StatusServ()




TYPE_PERSISTENT = Type()
# ["typeTemporary","typePersistent","Null","notNull","Issue01","PreemptLowerPriority","Never"]