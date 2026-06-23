# Persistence Intelligence

Messy Python research repo for exploring whether persistence is a useful
measurable property in audio signals.

The current goal is discovery, not framework design. Experiments should stay
small, visual, and easy to argue with.

## Current Hypothesis

Persistence is not a single quantity.

Early experiments suggest multiple forms of persistence may exist:

- Resonance Persistence
- Modal Persistence
- Recurrence Persistence
- Identity Persistence

The purpose of the project is to determine whether these can be unified under
a common mathematical framework.

## Shape

```text
persistence-intelligence/
├── notebooks/
├── persistence/
└── experiments/
```

- `notebooks/` holds sketchpad investigations.
- `persistence/` holds small reusable helpers that survived more than one pass.
- `experiments/` holds runnable scripts that produce plots or artifacts.

## Experiment 01

Run the first signal comparison:

```bash
python experiments/01_signal_persistence.py
```

Save the dashboard:

```bash
python experiments/01_signal_persistence.py --save experiments/01_signal_persistence.png
```

The old root launcher still works:

```bash
python persistence_experiment_01.py
```

## Current Experiments

```bash
python experiments/01_signal_persistence.py --save experiments/01_signal_persistence.png
python experiments/02_competing_resonances.py --save experiments/02_competing_resonances.png
python experiments/03_modal_objects.py --save experiments/03_modal_objects.png
python experiments/04_feedback_systems.py --save experiments/04_feedback_systems.png
python experiments/05_persistence_taxonomy.py --save experiments/05_persistence_taxonomy.png
```

Experiment 02 asks which frequency structures survive in a mixed signal.
Experiment 03 treats modes as physical objects after excitation.
Experiment 04 asks whether feedback persistence is recurrence, not just resonance.
Experiment 05 compares the measurements from Experiments 1-4 and asks whether
they form one family or several behaviors.

## Next Experiments

```bash
python experiments/17_causal_coupling_vs_common_excitation.py --save experiments/17_causal_coupling_vs_common_excitation.png
```

Experiment 17 asks whether the modes are actually causing one another, or
whether they are all being driven together by the same strike.

The planned sequence after that is:

- 17 Causal Coupling vs Common Excitation
- 18 Contact-Dynamics Excitation Model
- 19 Nonlinear Detuning / Frequency Pulling
- 20 First Generative Physical Model
