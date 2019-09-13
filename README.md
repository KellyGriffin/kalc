# kubectl-val

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![PyPI version](https://badge.fury.io/py/kubectl-val.svg)](https://badge.fury.io/py/kubectl-val) [![Build Status](https://travis-ci.org/criticalhop/kubectl-val.svg?branch=master)](https://travis-ci.org/criticalhop/kubectl-val)

# Overview

![kubernetes evicts](doc/img/kubernetes-evicts.png)

`kubectl-val` is a formal validator for whole kubernetes clusters' configurations using [AI planning](https://en.wikipedia.org/wiki/Automated_planning_and_scheduling). It is written in pure `Python` and translated to [PDDL](https://en.wikipedia.org/wiki/Planning_Domain_Definition_Language) using [poodle](https://github.com/criticalhop/poodle).

`kubectl-val` implements a simplified kubernetes model using an object-oriented state machine and searches for any scenario that may lead to a 'failure'. Failures are currently defined as `Service` having no associated running pods. Other definitions are also possible and are currently work in progress. 

# Quick Start

## Requirements

kubectl-val is written in modern Python and requires **Python 3.7+**, so please be prepared that if your default script installation  uses older Python versions you may have to manually specify the interpreter for the script.

## Installation

    $ pip install kubectl-val

`kubectl-val` comes as a simple [kubectl plugin](https://kubernetes.io/docs/tasks/extend-kubectl/kubectl-plugins/), so a working `kubectl` is a requirement if you want to access real cluster. If you do not have `kubectl` you can use it just as standalone shell command `kubectl-val` instead of `kubectl val ...`

## Usage

### Checking if creating a resource won't break anything

To try it against sample "broken" kubernetes configurations, use `-d` option to supply a folder with a collection of Kubernetes resources' stored from `kubectl get <...> -o=yaml > <...>.yaml`, and try to create a new resource with `-f`, e.g.:

    $ cd examples/daemonset-eviction
    $ kubectl val -d cluster-dump/ -f daemonset_create.yaml
    
### Checking a Kubernetes configuration for correctness

Invoking `kubectl val` without `-f` will run a check of current configuration and (hopefully) find no issues, as the configuration is already running. 

    $ kubectl val -d cluster-dump/

### Checking live cluster

Before checking the cluster you should first "dump" all of current resources into a "cluster dump" folder:

```shell
mkdir my-cluster-dump
cd my-cluster-dump
kubectl get nodes -o=yaml > nodes.yaml
kubectl get pods -o=yaml > pods.yaml
kubectl get services -o=yaml > services.yaml
kubectl get priority -o=yaml > priority.yaml
...
```

After you have the dump folder, you can continue with a check described above.

# Architecture

To search for a failure scenario, kubectl-val builds a model representation of the current cluster state that it reads from the files created by `kubectl get -o=yaml`. The constructed model is sent to PDDL planner and the resulting solution is then interpreted as a failure scenario and sent back to console as YAML-encoded scenario steps.

Scenario output can later be used by the pipeline operator to aid with decision making - e.g. whether stop the deployment, log the event to the dashboard, etc.

`kubectl-val` also calculates the probability of the scenario by multiplying the probability associated with every step.

![kubectl-val architecture](doc/img/architecture.png)

`kubectl-val` depends on a configured PDDL AI-planning `poodlesolver` running as http service. By default it uses a cloud solver hosted by [CriticalHop](https://www.criticalhop.com/). `poodlesolver` comes with `poodle` python library and installs automatically when `kubectl-val` is installed via `pip install`. To run a local solver, please refer to [poodle documentation](https://github.com/criticalhop/poodle). 

# Build from source

```shell
git clone https://github.com/criticalhop/kubectl-val
cd kubectl-val
poetry install
```

# Specifying solver location

If you run your own solver (recommended for testing purposes) - you can specify its URL with environment variable `POODLE_SOLVER_URL`:

```shell
export POODLE_SOLVER_URL=http://localhost:8082
```

# Vision

The goal for the project is to create an intent-driven, self-healing Kubernetes configuration system that will abstract the cluster manager from error-prone manual tweaking.

# Project Status

`kubectl-val` is a developer preview and currently supports a subset of resource/limits validation and partial label match validation.

We invite you to follow [@criticalhop](https://twitter.com/criticalhop) on [Twitter](https://twitter.com/criticalhop) and to chat with the team at [#kubectl-val](https://tinyurl.com/y5s98dw6) on [freenode](https://freenode.net/). If you have any questions or suggestions - feel free to open a [github issue](https://github.com/criticalhop/kubectl-val/issues) or contact andrew@criticalhop.com directly.

For enterprise enquiries, use the form on CriticalHop website: [criticalhop.com/demo](https://www.criticalhop.com/demo) or write us an email at info@criticalhop.com
