# SimpleSEDML
A simple API for using the [Simulation Experiment Description Markup Language (SED-ML)](https://sed-ml.org/), a community standard for describing simulation experiments.

The project provides a python interface to generating SED-ML based on the abstractions provided by [phraSED-ML](https://pmc.ncbi.nlm.nih.gov/articles/PMC5313123/pdf/nihms846540.pdf) to describe simulation experiments. These absractions are: (a) models (including changes in values of model parameters);
(b) simulations (including deterministic, stochastic, and steady state);
(c) tasks (which specify simulations to run on tasks and repetitions for changes in parameter values);
and (d) output for data reports and plots.

``SimpleSEDML`` generalizes the capabilities of ``PhraSEDML`` and simplifies its usage by exploiting the Python environment:

* A model source can be a file path or URL and may be in the Antimony language as well as SBML;
* Repeated tasks are defined more simply by the use of a ``pandas`` ``DataFrame``.
* Convenience methods are provided to simplify the API.
  
# Example

See this [Jupyter notebook](https://github.com/sys-bio/SimpleSEDML/blob/main/examples/usage_examples.ipynb) for a detailed example.

Consider the model below in the Antimony language.

    mymodel = """
    model myModel
        J1: S1 -> S2; k1*S1;
        k1 = 0.5;
    end
    """

We want to simulate this model and do a time course plot of all floating species in the model.

    from simple_sedml import SimpleSEDML

    sedml_str = SimpleSEDML.makeTimeCourse(mymodel)

We can print, save, or execute ``sedml_str``. To execute it,

    SimpleSEDML.executeSEDML(sedml_str)
<img src="docs/images/phrasedml_example.png" style="width:300px;height:300px;">

# Restrictions
1. If there are multiple task directives and/or there is a repeated task directive AND there is a report directive, SimpleSEDML.execute only returns the results of the last simulation. You can circumvent this by iterating in python to obtain the desired reports.

# Plans
1. First implementation of ``SimpleSEDML`` with methods for ``addModel``, ``addSimulation``, ``addTask``, ``addReport``, ``execute``, and ``to_sedml``.