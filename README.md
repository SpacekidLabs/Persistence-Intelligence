# Persistence Intelligence

Messy Python research repo for exploring whether persistence is a useful
measurable property in audio signals.

The current goal is discovery, not framework design. Experiments should stay
small, visual, and easy to argue with.

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
```

Experiment 02 asks which frequency structures survive in a mixed signal.
Experiment 03 treats modes as physical objects after excitation.
Experiment 04 asks whether feedback persistence is recurrence, not just resonance.
