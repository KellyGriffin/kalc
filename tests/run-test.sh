PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10000 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_0_run_pods_no_eviction_invload > log-synt-0
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10001 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_1_run_pods_with_eviction_invload > log-synt-1
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10002 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_2_synthetic_service_outage_invload > log-synt-2
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10003 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_3_synthetic_service_outage_multi_invload > log-synt-3
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10004 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_4_synthetic_service_NO_outage_multi > log-synt-4
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10005 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_synthetic_service_NO_outage_deployment_IS_outage > log-synt-4-1
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10006 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_5_evict_and_killpod_deployment_without_service > log-synt-5
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10007 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_6_evict_and_killpod_without_deployment_without_service > log-synt-6
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10008 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_7_evict_and_killpod_with_deployment_and_service > log-synt-7
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10009 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_8_evict_and_killpod_with_daemonset_without_service > log-synt-8
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10010 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_9_evict_and_killpod_with_daemonset_with_service > log-synt-9
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10011 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_10_startpod_without_deployment_without_service > log-synt-10
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10012 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_11_startpod_without_deployment_with_service > log-synt-11
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10013 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_12_startpod_with_deployment_with_service > log-synt-12
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10014 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_13_startpod_with_daemonset_without_service > log-synt-13
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10015 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_14_startpod_with_daemonset_with_service > log-synt-14
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10016 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_15_has_deployment_creates_daemonset__pods_evicted_pods_pending_synthetic > log-synt-15
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10017 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_16_creates_deployment_but_insufficient_resource__pods_pending_synthetic > log-synt-16
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10018 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_17_creates_service_and_deployment_insufficient_resource__service_outage > log-synt-17
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10019 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_17_2_creates_service_and_deployment_insufficient_resource__two_service_outage > log-synt-17-2
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10020 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_21_has_daemonset_creates_deployment__pods_evicted_daemonset_outage_synthetic > log-synt-21
PYTHON=pypy POODLE_SOLVER_URL=http://localhost:10021 tox -e poodledev -- ./tests/test_scenarios_synthetic.py::test_24_has_daemonset_with_service_creates_deployment__pods_evicted_daemonset_outage_synthetic_step3 > log-synt-24


