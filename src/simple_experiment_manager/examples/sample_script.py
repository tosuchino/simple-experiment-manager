from pathlib import Path

from simple_experiment_manager.manager import ExperimentManager
from simple_experiment_manager.schemas.contexts import ConfigClass, ExperimentContext

# 1. Instantiate the `ExperimentContext` class with your configuration.
# The experiment root is created at `base_dir /experiments`.
# All experiments are managed by the index file (JSON/YAML), `{index_file_name}`, under the experiment root.
# Each experiment has its own dedicated directory under the experiment root.
# Experiment configurations are managed by the config file (JSON/YAML), `{config_file_name}`, under each experiment directory.
default_config = ConfigClass(lr=1e-4, batch_size=32)
base_dir = Path.home() / "Documents" / "sample-simple-experiment-manager-script"
context = ExperimentContext(
    default_config=default_config,
    base_dir=base_dir,
)

# 2. Instantiate the `ExperimentManager`.
# This class provides various methods to manage experiments and labels.
# Each method returns a response schema containing a success flag, message and relevant objects.
manager = ExperimentManager(context)


def main() -> None:
    # Create a new experiment　with the default config
    print("\n--- Create a experiment ---")
    res_create_experiment = manager.create_experiment(name="exp_001")
    if res_create_experiment.is_success:
        print(res_create_experiment.message)
    else:
        print(res_create_experiment.message)

    # Check the currently active experiment
    print("\n--- Check the active experiment ---")
    if active_experiment := manager.active_experiment:
        print(f"Active experiment: {active_experiment}")
        print(f"Experiment directory path: {manager.active_experiment_dir}")
        print(f"Experiment config file path: {manager.active_experiment_config_file}")

    # Retrieve the configuration for the active experiment
    print("\n--- Retrieve the configuration for the active experiment ---")
    res_get_active_experiment_config = manager.get_active_experiment_config()
    if res_get_active_experiment_config.is_success:
        print(
            f"Configuration for the active experiment:\n{res_get_active_experiment_config.config}"
        )

    # Add new labels
    print("\n--- Add labels ---")
    label_names = ("label1", "label2")
    for lname in label_names:
        res_add_global_label = manager.add_global_label(name=lname)
        if res_add_global_label.is_success:
            print(res_add_global_label.message)

    # Display the global label list
    print("\n--- Show labels ----")
    global_labels = manager.global_labels
    print(f"Global labels: {global_labels}")

    # Assign a label to the active experiment
    if global_labels:
        label_to_add = next(iter(global_labels))
        print(
            f"\nAssign a label '{label_to_add}' to the active experiment: {manager.active_experiment}"
        )
        res_update_active_experiment_labels = manager.update_active_experiment_labels(
            labels={label_to_add}
        )
        if res_update_active_experiment_labels.is_success:
            print(res_update_active_experiment_labels.message)

    # Check the current label assignments
    print("\n--- Check label status for the active experiment ---")
    res_get_active_experiment_label_map = manager.get_active_experiment_label_map()
    if res_get_active_experiment_label_map.is_success:
        print(res_get_active_experiment_label_map.message)
        print(
            f"Labels for the active experiment: {res_get_active_experiment_label_map.label_map}"
        )

    # Copy a experiment
    print("\n--- Copy a experiment ---")
    res_copy_experiment = manager.copy_experiment(
        src_name="experiment1", dst_name="experiment2"
    )
    if res_copy_experiment.is_success:
        print(res_copy_experiment.message)

    # List all managed experiments
    print("\n--- List all experiments ---")
    print(f"Experiments: {manager.experiments}")

    # Check the current label usage statistics
    print("\n--- Check the label usage statistics ---")
    res_get_label_usage = manager.get_label_usage()
    if res_get_label_usage.is_success:
        print(res_get_label_usage.message)
        print(f"Label usage: {res_get_label_usage.usage}")

    print(
        f"\n[Cleanup Notice]\nAfter testing, manually delete the sample project directory: {manager.experiment_root.parent}"
    )


if __name__ == "__main__":
    main()
