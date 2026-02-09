import typer
from pydantic import BaseModel
from rich.syntax import Syntax
from rich.table import Table

from simple_experiment_manager.cli.editor import (
    build_template_dict_from_config_class,
    edit_config_via_editor,
    generate_yaml_string,
)
from simple_experiment_manager.cli.utils import (
    console,
    handle_result,
    initialize_context,
    resolve_manager,
)
from simple_experiment_manager.manager import ExperimentManager
from simple_experiment_manager.schemas.contexts import ExperimentContext

experiment_app = typer.Typer(
    help="Manage experiments: create, list, delete and rename."
)


@experiment_app.callback()
def callback(ctx: typer.Context) -> None:
    initialize_context(ctx)


@experiment_app.command(name="list")
def command_list_experiment(ctx: typer.Context):
    """Lists all experiments in the current library."""
    manager: ExperimentManager = resolve_manager(ctx)

    table = Table(
        title=f"Experiments in [bold cyan]{manager.ctx.experiment_root.parent.name}[/bold cyan]"
    )
    table.add_column("Active", justify="center", style="yellow")
    table.add_column("Name", style="magenta")
    table.add_column("Labels", style="green")

    for name in sorted(manager.experiments):
        is_active = "[bold]*[/bold]" if name == manager.active_experiment else ""

        # get labels via manager.index
        experiment_meta = manager.index.experiments.get(name) if manager.index else None
        labels = ", ".join(experiment_meta.labels) if experiment_meta else ""

        table.add_row(is_active, name, labels)

    console.print(table)


@experiment_app.command(name="create")
def command_create_experiment(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Experiment name to create."),
) -> None:
    """Creates a new experiment."""
    # experiment context
    manager: ExperimentManager = resolve_manager(ctx)
    experiment_ctx: ExperimentContext = manager.ctx

    # validate experiment existence
    if name in manager.experiments:
        handle_result(is_success=False, message=f"Experiment '{name}' already exists.")

    # edit config instance via editor
    data = build_template_dict_from_config_class(experiment_ctx.default_config)
    config_inst = edit_config_via_editor(ctx=experiment_ctx, data=data)

    # run and show the result
    res = manager.create_experiment(name=name, config=config_inst)
    handle_result(is_success=res.is_success, message=res.message)


@experiment_app.command(name="rename")
def command_rename_experiment(
    ctx: typer.Context,
    old_name: str = typer.Argument(..., help="Current experiment name."),
    new_name: str = typer.Argument(..., help="New experiment name."),
):
    """Rename an existing experiment."""
    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.rename_experiment(old_name=old_name, new_name=new_name)
    handle_result(is_success=res.is_success, message=res.message)


@experiment_app.command(name="delete")
def command_delete_experiment(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Experiment name to delete."),
    force: bool = typer.Option(
        False, "--force", "-f", help="Delete without confirmation."
    ),
):
    """Delete a experiment and its directory."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete '{name}'?")
        if not confirm:
            raise typer.Abort()

    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.delete_experiment(name)
    handle_result(is_success=res.is_success, message=res.message)


@experiment_app.command(name="switch")
def command_switch_experiment(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The experiment name to switch."),
):
    """Swithes the active experiment."""
    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.set_active_experiment(name)
    handle_result(is_success=res.is_success, message=res.message)


@experiment_app.command(name="show")
def command_show_experiment(ctx: typer.Context):
    """Shows the configuration for the active experiment."""
    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.get_active_experiment_config()
    if res.is_success and res.config:
        config = res.config
        if isinstance(config, BaseModel):
            data = config.model_dump(mode="json")
        else:
            data = config.to_dict(mode="json")
        yaml_str = generate_yaml_string(ctx=manager.ctx, data=data)
        console.print(
            f"\n[bold cyan]Experiment:[/bold cyan] {manager.active_experiment}"
        )
        console.print(Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True))
    else:
        handle_result(is_success=res.is_success, message=res.message)


@experiment_app.command(name="update")
def command_update_experiment(ctx: typer.Context):
    """Edits the active experiment's configuration."""
    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.get_active_experiment_config()

    if not res.is_success or res.config is None:
        handle_result(False, res.message)
        return

    # update config via the editor
    data = build_template_dict_from_config_class(res.config)
    new_config = edit_config_via_editor(ctx=manager.ctx, data=data)

    update_res = manager.update_active_experiment_config(new_config)
    handle_result(update_res.is_success, update_res.message)


@experiment_app.command(name="copy")
def command_copy_experiment(
    ctx: typer.Context,
    src_name: str = typer.Argument(..., help="The experiment name to copy from."),
    dst_name: str = typer.Argument(..., help="The experiment name to copy to."),
):
    """Creates a new experiment by copying an existing one."""
    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.copy_experiment(src_name=src_name, dst_name=dst_name)
    handle_result(is_success=res.is_success, message=res.message)
