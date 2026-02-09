from pathlib import Path

import typer

from simple_experiment_manager.cli.experiment import experiment_app
from simple_experiment_manager.cli.label import label_app
from simple_experiment_manager.manager import ConfigClass, ExperimentManager
from simple_experiment_manager.schemas.contexts import ExperimentContext

# Main app
main_app = typer.Typer(
    help="Sample CLI for using simple-experiment-manager.\n\n"
    "Note: This sample creates a directory at "
    "~/Documents/sample-simple-experiment-manager-cli.\n"
    "Please delete it manually after testing."
)

# Add experiment and label commands
main_app.add_typer(experiment_app, name="experiment")
main_app.add_typer(label_app, name="label")


@main_app.callback()
def setup(ctx: typer.Context):
    # Initialize `ExperimentContext` with your configuration and base directory path.
    # This configuration creates the experiment root at `base_dir / experiments`.
    default_config = ConfigClass(lr=1e-4, batch_size=32)
    base_dir = Path.home() / "Documents" / "sample-simple-experiment-manager-cli"
    experiment_ctx = ExperimentContext(
        default_config=default_config,
        base_dir=base_dir,
    )

    # Initialize `ExperimentManager`, which provides the core API functions for experiment management.
    manager = ExperimentManager(experiment_ctx)

    # Inject the `ExperimentManager` instance into `ctx.obj` for use by subcommands.
    ctx.obj = {"experiment_manager": manager}


if __name__ == "__main__":
    # [Cleanup Notice]
    # After testing, manually delete: ~/Documents/sample-simple-experiment-manager-cli
    main_app()
