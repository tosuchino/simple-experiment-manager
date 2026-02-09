# Simple Experiment Manager

A simple experiment management framework to handle experiment-specific configurations with an integrated CLI and APIs.

## 🌟 Features

- **Flexible Configuration**: Define your experiment configuration by keyword arguments or your Pydantic model.
- **Smart CLI**: Auto-generated YAML templates with comment-based help.
- **Experiment Management**: Easily create, rename, copy, switch, show, and delete experiments.
- **Labeling System**: Organize experiments with global labels.

## 📦 Directory Structure

The manager organizes files under your base directory (default: `~/Documents/simple_experiment_manager`):

```text
Documents/
└── simple_experiment_manager/       # base_dir
    └── experiments/                 # experiment_root (experiment_root_name)
        ├── experiment_index.json    # Global experiment index and labels
        ├── experiment_001/          # Individual experiment directory
        │   └── config.yaml          # Experiment-specific configuration
        └── experiment_002/
            └── config.yaml
```

## 🛠 Installation

### Environment

- **Python**: 3.10+
- [**uv**](https://docs.astral.sh/uv/)

### Setup

```shell
# Install all dependencies
uv sync
```

## 🚀 Quick start

### 1. Setup the Context

Setup your experiment context, please refer to [Data Structure](#-data-structure) for details.

```python
from pathlib import Path

from simple_experiment_manager.schemas.contexts import ConfigClass, ExperimentContext

default_config = ConfigClass(lr=1e-4, batch_size=32)
base_dir = Path.home() / "Documents" / "my_project" # experiment root is given by `base_dir / experiments`

experiment_ctx = ExperimentContext(
    default_config=default_config,
    base_dir=base_dir,
)
```

For details on the definition of experiment configuration, see [Default Configuration](#-default-configuration).

### 2. Use in Your Scripts (API)

The ExperimentManager provides a high-level API to access experiment data and paths. Please refer to [Core API](#-core-api) for details.

```python
from simple_experiment_manager.manager import ExperimentManager

manager = ExperimentManager(experiment_ctx)

# Access experiment properties
print(f"Active Experiment: {manager.active_experiment}")
print(f"Config Path: {manager.active_experiment_config_file}") # absolute path
print(f"Experiment Dir: {manager.active_experiment_dir}") # absolute path

# Retrieve the configuration instance
res = manager.get_active_experiment_config()
if res.is_success and res.config:
    config = res.config  # Fully type-hinted MyConfig instance
    # run_simulation(config)
```

For a comprehensive demonstration of API, checkout [examples/sample_script.py](src/simple_experiment_manager/examples/sample_script.py):

```shell
uv run python -m simple_experiment_manager.examples.sample_script
```

This generates the experiment index file (`experiment_index.json`) as:

```json
{
  "active_experiment": "exp_001",
  "global_labels": ["label1", "label2"],
  "experiments": {
    "exp_001": {
      "created_at": "2026-02-22T16:14:53.443904",
      "labels": ["label1"],
      "config_path": "exp_001/config.yaml"
    }
  }
}
```

and the configuration file (`exp_001/config.yaml`) as:

```yaml
lr: 0.0001
batch_size: 32
```

After testing the above sample script, please manually delete the sample project directory: `~/Documents/sample-simple-experiment-manager-script`

### 3. Integrate with CLI (Typer Example)

Integrate the provided `experiment_app` and `label_app` to your `Typer` instance.

```python
import typer
from simple_experiment_manager.manager import ExperimentManager
from simple_experiment_manager.cli.experiment import experiment_app
from simple_experiment_manager.cli.label import label_app

main_app = typer.Typer()
main_app.add_typer(experiment_app, name="experiment")
main_app.add_typer(label_app, name="label")

@main_app.callback()
def setup(ctx: typer.Context):
    # Initialize `ExperimentManager`, which provides the core API functions for experiment management.
    manager = ExperimentManager(experiment_ctx)
    # Inject the `ExperimentManager` instance into `ctx.obj` for use by subcommands.
    ctx.obj = {"experiment_manager": manager}

if __name__ == "__main__":
    main_app()
```

For a comprehensive demonstration of CLI, checkout [examples/sample_cli.py](src/simple_experiment_manager/examples/sample_cli.py):

```shell
uv run python -m simple_experiment_manager.examples.sample_cli --help
```

After testing the above sample script, please manually delete the sample project directory: `~/Documents/sample-simple-experiment-manager-cli`

## 📝 Reference

### 📋 Data Structure

`ExperimentContext` [[source]](src/simple_experiment_manager/schemas/contexts.py)

A configuration object required to initialize the `ExperimentManager`.

#### Parameters:

- default_config (BaseModel | ConfigClass): Your model for experiment settings.
- base_dir (Path): Parent directory of the experiment root (default: ~/Documents/simple_experiment_manager).
- experiment_root_name: Root directory name for experiments (default: experiments).
- config_file_name (str): Filename for experiment settings (default: config.yaml).
- index_file_name (str): Filename for the global index (default: experiment_index.json).

### 📝 Default Configuration

Users can define quickly the default configuration object by using `ConfigClass` as shown above:

```python
from simple_experiment_manager.schemas.contexts import ConfigClass, ExperimentContext

default_config = ConfigClass(lr=1e-4, batch_size=32)

experiment_ctx = ExperimentContext(default_config=default_config)
```

A `Pydantic` class is also available for the default configuration. The adoption of the `Pydantic` class provides auto validations and descriptions:

```python
from typing import Annotated

from pydantic import BaseModel, Field

from simple_experiment_manager.schemas.contexts import ExperimentContext

class MyConfig(BaseModel):
    lr: Annotated[float, Field(gt=0.0, description="learning rate")] = Field(default=1e-4)
    batch_size: Annotated[int, Field(gt=0, description="batch size")] = Field(default=32)

default_config = MyConfig()

experiment_ctx = ExperimentContext(default_config=default_config)
```

The config file is generated as follows:

```yaml
# learning rate
lr: 0.0001
# batch size
batch_size: 32
```

Note that the comments in the config yaml file are only added to top level fields.

### 📝 Core API

`ExperimentManager` [[source]](src/simple_experiment_manager/manager.py)

The primary interface for experiment operations.

#### Parameters:

- ctx (`ExperimentContext`): An instance of ExperimentContext defining the environment.

#### Properties

- `active_experiment`: Returns the name of the currently active experiment (`str | None`).
- `active_experiment_dir`: Returns the absolute `Path` to the active experiment folder.
- `active_experiment_config_file`: Returns the absolute `Path` to the active experiment's config file.
- `experiments`: Returns a `set` of all registered experiment names.
- `global_labels`: Returns a `set` of all registered global labels.

#### Key Methods

- `create_experiment(name, config)`: Initializes a new experiment directory and config.
- `set_active_experiment(name)`: Switches the current active context.
- `get_active_experiment_config()`: Returns the validated config instance of the active experiment.
- `update_active_experiment_config(config)`: Updates the active experiment's config file.
- `copy_experiment(src, dst)`: Duplicates an existing experiment.
- `delete_experiment(name)`: Deletes a experiment directory and removes it from the index.
- `rename_active_experiment(new_name)`: Renames the active experiment name.
- `add_global_label(name)`: Adds a new label to the global label set.
- `remove_global_label(name)`: Removes a label from the global label set and from all the experiments.
- `update_active_experiment_labels(labels)`: Updates labels for the currently active experiment.
- `get_label_usage()`: Returns a mapping of labels to the experiments using them.
- `get_active_experiment_label_map()`: Gets a map of all global labels and whether they are assigned to the active experiment.

## 🛠 CLI Commands

### Experiment Management (experiment)

- **list**: List all experiments with their active status and labels.
- **create**: Create a new experiment (opens editor if defaults are insufficient).
- **switch**: Set a specific experiment as the active one.
- **update**: Re-edit the active experiment's configuration in your editor.
- **show**: Display the active configuration with YAML syntax highlighting.
- **rename**: Rename an existing experiment.
- **copy**: Create a new experiment by copying an existing one.
- **delete**: Delete an experiment directory and its index entry.

### Label Management (label)

- **list**: Show global labels and usage counts. Use --verbose to see experiment names.
- **add**: Register a new label globally.
- **assign**: Assign/unassign labels to the active experiment via a YAML-based checkbox editor.
- **remove**: Delete a label from the global list and all assigned experiments.
