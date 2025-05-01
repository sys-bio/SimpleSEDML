# SimpleSEDML
A simple API for using the [Simulation Experiment Description Markup Language (SED-ML)](https://sed-ml.org/), a community standard for describing simulation experiments.

The project exposes an programmatic interface to the textual capabilities provided by [phraSED-ML](https://pmc.ncbi.nlm.nih.gov/articles/PMC5313123/pdf/nihms846540.pdf) to describe simulation experiments. ``SimpleSEDML`` uses the abstractions provided by ``phraSED-ML`` to generate and validate ``SED-ML``.
PhraSEDML is a human-readable language designed for creating simulation experiment descriptions that can be converted to SED-ML (Simulation Experiment Description Markup Language). It serves as an easier way to author SED-ML files, which are XML-based documents used to describe computational experiments in systems biology.
Key features of PhraSEDML include:

* Human-Readable Syntax: Much easier to write and understand than raw XML-based SED-ML
Core Components:

* Model definitions (references to SBML models)
Simulation settings (time courses, steady state analyses)
Task definitions (running simulations on models)
Output specifications (plots, reports)


* Integration with Tellurium: In the Tellurium Python package, PhraSEDML scripts can be written and then converted to SED-ML using the phrasedml.convertString() function
Model References: Uses phrasedml.setReferencedSBML() to link models mentioned in PhraSEDML to actual SBML model content
Execution: After conversion to SED-ML, simulations can be executed using functions like te.executeSEDML()

* PhraSEDML simplifies the process of creating reproducible computational experiments in systems biology by providing a more intuitive syntax that gets converted to standard SED-ML files for broader compatibility with simulation tools.
  
For example, consider the model below in the Antimony language.

model myModel
    J1: S1 -> S2; k1*S1;
    k1 = 0.5;
end

We want to simulate this model and plot the species ``S1``, ``S2``.
To do this, we use the following ``phraSEDML`` directives:

    // Define the model being usede
    model1 = model "myModel"
    
    // Define simulation settings 
    sim1 = simulate uniform(0, 20, 100) // time 0 to 20, 100 points
    
    // Define task
    task1 = run sim1 on model1
    
    // Define output
    plot "Conversion of S1 to S2" time vs S1, S2
    report time vs S1, S2

And let ``sbml_str`` be this model in the [SBML](https://pmc.ncbi.nlm.nih.gov/articles/PMC8411907/) representation.
The following ``Python`` code executes the ``phraSEDML`` directives:

    import tellurium as te # get the Tellurium simulator

    sedml_str = phrasedml.convertString(phrasedml_str)
    # Set the reference to the SBML model
    phrasedml.setReferencedSBML("myModel", sbml_str)

    # Convert PhraSEDML to SED-ML
    sedml_str = phrasedml.convertString(phrasedml_str)

    # Execute SED-ML
    if sedml_str:
        te.executeSEDML(sedml_str)
    else:
        # Error in the directives
        print(phrasedml.getLastPhrasedError())


The output is
<img src="docs/images/phrasedml_example.png" alt="Girl in a jacket" style="width:300px;height:300px;">

# Plans
1. Replicate the functions of the text-based ``phraSEDML`` in ``SimpleSEDML``. The implementation should allow for the concurrent construction of multiple ``SimpleSEDML`` objects, something that is not possible the ``phrasedml``.
2. Extend Model by allowing descriptions: (a) automatically convert Antimony into SBML, (b) can reference arbitrary paths to local files, (c) allow URL access.
3. Extend Simulate to report model errors that are detectable without running a simulation.