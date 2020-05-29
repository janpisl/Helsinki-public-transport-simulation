Helsinki public transport simulation
====================================


Modeling public transportation in Helsinki area to identify parts vulnerable to delays caused by congestion


Installing
----------

Install directly to your current python environment for GitHub master branch:

python3 -m pip install get+https://github.com:jarmokivekas/transit_simulation.git


Obtaining a Copy for Development
--------------------------------

Clone the repo from GitHub.

```sh
# clone (or extract the source distribuiiton archive)
git clone git@github.com:janpisl/Helsinki-public-transport-simulation.git
cd Helsinki-public-transport-simulation
# install the venv package if you don't have it
python3 -m pip install venv
# create and activate the virtualenv
python3 -m venv .venv
source .venv/bin/activate
# make sure you pip is up-to-date
python3 -m pip install pip -U
# install all required packages into the virtualenv
python3 -m pip install .
# to make sure everything works, run the test suite
make test
```
