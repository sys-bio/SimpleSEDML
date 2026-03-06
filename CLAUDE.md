# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SimpleSEDML is a Python library that provides a simplified API for creating [SED-ML](https://sed-ml.org/) simulation experiment descriptions. It wraps [phraSED-ML](https://pmc.ncbi.nlm.nih.gov/articles/PMC5313123/pdf/nihms846540.pdf) and [tellurium](https://tellurium.readthedocs.io/) to generate, validate, and execute SED-ML/OMEX files for systems biology models.

## Commands

### Install
```bash
pip install -e .
# or install all dependencies:
pip install -r requirements.txt
```

### Run tests
```bash
# Run all tests
python -m pytest src/tests/

# Run a single test file
python -m pytest src/tests/test_single_model_time_course.py

# Run a single test
python -m pytest src/tests/test_single_model_time_course.py::TestSingleModelTimeCourse::test_init

# Using nose2
python -m nose2 -s src/tests
```

**Note:** Many test files have `IGNORE_TEST = True` at the top with individual tests decorated with `@unittest.skipIf(IGNORE_TEST, "...")`. Set `IS_PLOT = False` in test files to suppress plot windows during testing.

### Build and distribute
```bash
python3 -m build --verbose
python3 -m twine upload dist/*
# (PyPI API token must be configured in ~/.pypirc)
```

## Architecture

### Class Hierarchy

The library is organized around a core `SimpleSEDML` class that maps directly to phraSED-ML concepts:

```
SimpleSEDML (simple_sedml.py)        ← Core class, manages dicts of SED-ML components
├── SingleModelTimeCourse             ← Single model time course (convenience wrapper)
├── MultipleModelSimpleSEDML          ← Abstract base for multi-model tasks
│   ├── MultipleModelTimeCourse       ← Compare multiple models over time
│   └── MultipleModelParameterScan    ← Scan parameters across multiple models
└── SingleModelParameterScan          ← Parameter scan for a single model

Executor (executor.py)                ← Non-SEDML execution using roadrunner directly
```

### SED-ML Component Modules

Each SED-ML construct has its own module:
- `model.py` — `Model`: resolves model refs (Antimony string/file, SBML string/file/URL) to SBML files in `project_dir`
- `simulation.py` — `Simulation`: uniform, stochastic, steadystate, onestep
- `task.py` — `Task`, `RepeatedTask`: tasks and parameter sweeps
- `plot.py` — `Plot`: 2D plot specifications
- `report.py` — `Report`: tabular output specifications
- `variable_collection.py` — `VariableCollection`: manages display variables and scan parameters, handles scoping (`task_id.variable_name`)
- `omex_maker.py` — `OMEXMaker`: creates COMBINE archive (.omex) files
- `model_information.py` — `ModelInformation`: introspects SBML/Antimony models for parameters and species

### Data Flow

1. User calls `SimpleSEDML.add*()` methods to build component dictionaries (`model_dct`, `simulation_dct`, `task_dct`, etc.)
2. `getPhraSEDML()` assembles all components into a phraSED-ML string
3. `getSEDML()` calls `phrasedml.convertString()` to produce SED-ML XML, then patches display names
4. `execute()` calls `tellurium.executeSEDML()` on the resulting SED-ML

**Alternative path:** `Executor` bypasses SED-ML/phraSED-ML entirely, using roadrunner directly via `model.roadrunner` for `executeTask()` and `executeRepeatedTask()`.

### Variable Scoping

Variables in phraSED-ML are scoped by task: `task_id.variable_name` (using `cn.SCOPE_INDICATOR = "."`). `VariableCollection` manages the mapping between scoped names, unscoped names, and display names. When multiple models/tasks are used, curve legend labels use the model name prefix (e.g., `md_modelname`) stripped of the `PREFIX_LEN`-char prefix.

### Model Reference Types (`constants.py`)

- `"ant_str"` — Antimony model string (default)
- `"sbml_str"` — SBML XML string
- `"sbml_file"` — path to SBML file
- `"ant_file"` — path to Antimony file
- `"sbml_url"` — URL to SBML file
- `"model_id"` — ID of a previously defined model (for parameter variants)

### Project Directory

Each `SimpleSEDML` instance writes model SBML files to a `project_dir` (default: `"project/"`). `cleanUp()` removes this directory. Model files are written during `Model.__init__()`.

### Key Constants (`constants.py`)

ID prefixes used internally: `md_` (model), `si_` (simulation), `ta_` (task), `rt_` (repeated task), `st_` (subtask), `re_` (report), `pl_` (plot). All prefixes have `PREFIX_LEN = 3` characters.

Simulation types: `"uniform"` (CVODE), `"uniform_stochastic"` (Gillespie), `"steadystate"`, `"onestep"`.

## Known Restrictions

1. When there are multiple task/repeated task directives AND a report directive, `execute()` only returns results from the last simulation.
2. Steadystate simulations don't execute correctly via `execute()` (phraSED-ML issue), but do generate valid SED-ML.
3. `SimpleSEDML.validate()` is not yet implemented.
