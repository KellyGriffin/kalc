from random import randrange
import os
import re


comment = "cost250-500-poodle29e0e61-inparallelway"
file_for_commit = "./log-current-commit"
file_for_poodle_commit = "./log-current-commit_poodle" 
file_for_list_of_reports = "./log_list_of_reports"
lin_count = "50"
weight = "1"

domain_high_cost = 3000
domain_middle_cost = 250
timeout = 1000
list_of_evaluators = ['--evaluator "hff=ff()" --evaluator "hlm=lmcount(lm_rhw(reasonable_orders=true))"',\
                      '--evaluator "hlm=lmcount(lm_rhw(reasonable_orders=true),transform=adapt_costs(normal))" --evaluator "hff=ff(transform=adapt_costs(normal))"']
list_of_search_engines = ['lazy_wastar(list(hff, hlm), preferred = list(hff, hlm)',\
                          'lazy(alt([single(hff),single(hff,pref_only=true),single(hlm),single(hlm,pref_only=true),type_based([hff,g()])],boost=1000),preferred=[hff,hlm],cost_type=normal,reopen_closed=false,randomize_successors=true,preferred_successors_first=false,bound=infinity']
search_evaluators = list_of_evaluators[1] 
search_engine = list_of_search_engines[0]

poodle_rel_path = "../poodle/"
kubectl_rel_path_from_poodle = "../kubectl-val/"
test_cases =[]
test_file = "test_synthetic_hypothesis_run.py"
with open("./tests/"+test_file) as f_test:
    test_file_lines = f_test.read().splitlines()

for test_line_item in test_file_lines:
    if "def" in test_line_item and "test_" in test_line_item:
        test_cases.extend([test_line_item.replace("def","").replace("():","").strip()])




command_to_get_git_commit = "git rev-parse --short HEAD >"+ file_for_commit + "; git branch | grep \* | cut -d ' ' -f2 >> " + file_for_commit
os.system(command_to_get_git_commit)
commit_item = ['']
with open(file_for_commit) as f_commit:
    commit_item = f_commit.read().splitlines()

commit_item_inline= ''
for line in commit_item:
     commit_item_inline = commit_item_inline + line + '-'

command_to_get_git_commit_poodle = "cd "+ poodle_rel_path + "; git rev-parse --short HEAD > " + kubectl_rel_path_from_poodle + file_for_poodle_commit + "; git branch | grep \* | cut -d ' ' -f2 >> " + file_for_poodle_commit
os.system(command_to_get_git_commit_poodle)
commit_poodle_item = ['']
with open(file_for_poodle_commit) as f_commit_poodle:
    commit_poodle_item = f_commit_poodle.read().splitlines()

commit_poodle_item_inline= ''
for line in commit_poodle_item:
     commit_poodle_item_inline = commit_poodle_item_inline + line + '-'

print(commit_poodle_item_inline)

from datetime import datetime
    
for i in test_cases:
    test_name = i
    random_number = randrange(100, 900, 1)
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    log_id = str(now) + str(random_number)
    log_params = [log_id, comment, commit_item_inline, commit_poodle_item_inline, test_file, test_name, lin_count, weight, timeout]
    print(log_params)
    f_report_list = open(file_for_list_of_reports,"a+")
    f_report_list.write(str(log_params) +"\r\n")
    log_name = "log-" + log_id
    port = randrange(10000, 10101, 1) 
    template = "SEARCH_EVALUATORS='{}' SEARCH_ENGINE='{}' TIMEOUT={} DOMAIN_HIGH_COST={} DOMAIN_MIDDLE_COST={} OUT_NAME={} POODLE_LIN_COUNT={} POODLE_ASTAR_WEIGHT={} PYTHON=pypy POODLE_SOLVER_URL=http://localhost:{} tox -e poodledev -- -s ./tests/{}::{} > {}"
    print(template.format(search_evaluators, search_engine, timeout, domain_high_cost, domain_middle_cost, log_name, lin_count, weight, port, test_file, test_name, log_name))
    bashCommand = template.format(search_evaluators, search_engine, timeout, domain_high_cost, domain_middle_cost, log_name, lin_count, weight, port, test_file, test_name, log_name)
    os.system(bashCommand)
