from pathlib import Path

from simple_experiment_manager.manager import ExperimentManager
from simple_experiment_manager.schemas.contexts import ConfigClass, ExperimentContext
from simple_experiment_manager.schemas.responses import ExperimentManagerResponse

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


def handle_res_message(res: ExperimentManagerResponse) -> None:
    pre_msg = "Success" if res.is_success else "Error"
    print(f"{pre_msg}: {res.message}")


def main() -> None:
    # Create a new experiment　with the default config
    print("\n--- Create a new experiment ---")
    res_create_experiment = manager.create_experiment(name="exp_001")
    handle_res_message(res_create_experiment)

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
    handle_res_message(res_get_active_experiment_config)

    # Add labels to the active experiment
    print("\n--- Add labels to the active expriment ---")
    labels = ["label1", "label2", "label3"]
    res_add_global_label = manager.add_labels_to_active_experiment(labels=labels)

    handle_res_message(res_add_global_label)

    # Display the global label list
    print("\n--- Show the global labels ----")
    global_labels = manager.global_labels
    print(f"Global labels: {global_labels}")

    # Check the current label assignments
    print("\n--- Check the label status for the active experiment ---")
    res_get_active_experiment_label_map = manager.get_active_experiment_label_map()
    if res_get_active_experiment_label_map.is_success:
        print(
            f"Labels for the active experiment: {res_get_active_experiment_label_map.label_map}"
        )
    handle_res_message(res_get_active_experiment_label_map)

    # Copy a experiment
    print("\n--- Copy an experiment ---")
    res_copy_experiment = manager.copy_experiment(
        src_name="exp_001", dst_name="exp_002"
    )
    handle_res_message(res_copy_experiment)

    # Assign labels to the active experiment
    print("\n--- Assign labels to the active experiment ---")
    if global_labels:
        labels_to_add = [
            "label1",
            "label2",
        ]  # "label3" is removed from the active experiment
        print(
            f"\nAssign a label '{labels_to_add}' to the active experiment: {manager.active_experiment}"
        )
        res_update_active_experiment_labels = manager.update_active_experiment_labels(
            labels=labels_to_add
        )
        handle_res_message(res_update_active_experiment_labels)

    # List all managed experiments
    print("\n--- List all experiments ---")
    print(f"Experiments: {manager.experiments}")

    # Check the current label usage statistics
    print("\n--- Check the label usage statistics ---")
    res_get_label_usage = manager.get_label_usage()
    if res_get_label_usage.is_success:
        print(f"Label usage: {res_get_label_usage.usage}")

    handle_res_message(res_get_label_usage)

    print(
        f"\n[Cleanup Notice]\nAfter testing, manually delete the sample project directory: {manager.experiment_root.parent}"
    )


if __name__ == "__main__":
    main()
