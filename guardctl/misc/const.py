from poodle import Object
from guardctl.model.system.primitives import StatusServ, StatusNode, StatusPod, StatusLim, StatusSched, StatusReq, Type

STATUS_LIM_MET = "Limit is met"
STATUS_LIM_EXCEEDED = "LImits is exceded"
STATUS_POD_FAILED =  "Inactive"
STATUS_POD_KILLING = "Killing"
STATUS_POD_PENDING = "Pending" 
STATUS_POD_RUNNING = "Running"
STATUS_NODE_ACTIVE = "Active"
STATUS_NODE_INACTIVE = "Inactive"
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
STATUS_SCHED_CHANGED =  "Changed"
STATUS_SCHED_CLEAN   =  "Clean"
STATUS_SERV_INTERRUPTED = "Interrupted"
STATUS_SERV_PENDING = "Pending"
STATUS_SERV_STARTED = "Started"



TYPE_POLICY_PreemptLowerPriority = "PreemptLowerPriority"
TYPE_POLICY_NEVER = "Never"
