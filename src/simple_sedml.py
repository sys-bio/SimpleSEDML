import phrasedml # type: ignore
import tellurium as te  # type: ignore

class Model:
    def __init__(self, id, source):
        self.id = id
        self.source = source
        self.param_changes = []

    def set_parameter(self, param_id, value):
        self.param_changes.append((param_id, value))

    def to_string(self):
        if not self.param_changes:
            return f'{self.id} = model "{self.source}"'
        params = ", ".join(f"{param} = {val}" for param, val in self.param_changes)
        return f'{self.id} = model "{self.source}" with {params}'


class Simulation:
    def __init__(self, id, start, end, steps, algorithm=None):
        self.id = id
        self.start = start
        self.end = end
        self.steps = steps
        self.algorithm = algorithm

    def to_string(self):
        lines = [f'{self.id} = simulate uniform({self.start}, {self.end}, {self.steps})']
        if self.algorithm:
            lines.append(f'{self.id}.algorithm = "{self.algorithm}"')
        return "\n".join(lines)


class Task:
    def __init__(self, id, model, simulation):
        self.id = id
        self.model = model
        self.simulation = simulation

    def to_string(self):
        return f'{self.id} = run {self.simulation} on {self.model}'


class RepeatedTask:
    def __init__(self, id, changes, subtask, reset=True, nested_repeats=None):
        self.id = id
        self.changes = changes  # list of (target, range_expr)
        self.subtask = subtask  # can be a Task or another RepeatedTask
        self.reset = reset
        self.nested_repeats = nested_repeats or []  # list of RepeatedTask

    def to_string(self):
        lines = []
        for nested in self.nested_repeats:
            lines.append(nested.to_string())
        assignments = ", ".join(f"{target} in {expr}" for target, expr in self.changes)
        reset_str = ", reset=true" if self.reset else ""
        lines.append(f'{self.id} = repeat {self.subtask.id} for {assignments}{reset_str}')
        return "\n".join(lines)


class Plot2D:
    def __init__(self, title):
        self.title = title
        self.curves = []

    def add_curve(self, x, y):
        self.curves.append((x, y))

    def to_string(self):
        return "\n".join([f'plot "{self.title}" {x} vs {y}' for x, y in self.curves])


class Experiment:
    def __init__(self):
        self.models = []
        self.simulations = []
        self.tasks = []
        self.repeated_tasks = []
        self.plots = []

    def add_model(self, model):
        self.models.append(model)

    def add_simulation(self, simulation):
        self.simulations.append(simulation)

    def add_task(self, task):
        self.tasks.append(task)

    def add_repeated_task(self, rtask):
        self.repeated_tasks.append(rtask)

    def add_plot(self, plot):
        self.plots.append(plot)

    def to_string(self):
        sections = [
            *[m.to_string() for m in self.models],
            *[s.to_string() for s in self.simulations],
            *[t.to_string() for t in self.tasks],
            *[rt.to_string() for rt in self.repeated_tasks],
            *[p.to_string() for p in self.plots],
        ]
        return "\n".join(sections)




#from phrasedml_api import Model, Simulation, Task, RepeatedTask, Plot2D, Experiment # type: ignore
import tellurium as te

# Define the model
model1 = Model("model1", source="BIOMD0000000012")
model1.set_parameter("ps_b", 0.02)

# Define the simulation
sim1 = Simulation("sim1", start=0, end=1000, steps=1000, algorithm="CVODE")

# Define the base task
task1 = Task("task1", model="model1", simulation="sim1")

# Inner repeated task (e.g., scan ps_0)
inner_scan = RepeatedTask(
    id="inner_scan",
    changes=[("model1.ps_0", "uniform(0.01, 0.05, 3)")],
    subtask=task1,
    reset=True
)

# Outer repeated task (e.g., scan ps_a) nesting inner_scan
outer_scan = RepeatedTask(
    id="outer_scan",
    changes=[("model1.ps_a", "uniform(0.1, 0.3, 2)")],
    subtask=inner_scan,
    reset=True,
    nested_repeats=[inner_scan]
)

# Plotting results
plot = Plot2D("Nested scan of ps_0 and ps_a")
plot.add_curve(x="task1.time", y="task1.PX")
plot.add_curve(x="outer_scan.time", y="outer_scan.PX")

# Assemble everything
exp = Experiment()
exp.add_model(model1)
exp.add_simulation(sim1)
exp.add_task(task1)
exp.add_repeated_task(outer_scan)
exp.add_plot(plot)

# Print phraSED-ML
import pdb; pdb.set_trace()
rr = te.loadSBMLModel("BIOMD0000000012")
phrasedml.setReferencedSBML("myModel", sbml_str)

# Convert phrasedml to SED-ML
sedml_str = phrasedml.convertString(phrasedml_str)
print(exp.to_string())