import typer

from simple_experiment_manager.cli.editor import edit_label_map_via_editor
from simple_experiment_manager.cli.utils import (
    console,
    handle_result,
    initialize_context,
    resolve_manager,
)
from simple_experiment_manager.manager import ExperimentManager

label_app = typer.Typer(help="Manage global labels and experiment assignments.")


@label_app.callback()
def callback(ctx: typer.Context) -> None:
    initialize_context(ctx)


@label_app.command(name="list")
def command_list_labels(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show experiment names using each label."
    ),
):
    """List global labels and their usage statistics."""
    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.get_label_usage()  # get label usage

    if not res.is_success:
        handle_result(False, res.message)
        return

    from rich.table import Table

    table = Table(title="Global Label Usage", header_style="bold magenta")
    table.add_column("Label", style="cyan")
    table.add_column("Usage Count", justify="right", style="green")

    if verbose:
        table.add_column("Experiments", style="yellow")

    for label, experiments in sorted(res.usage.items()):
        row = [label, str(len(experiments))]
        if verbose:
            row.append(", ".join(sorted(list(experiments))))
        table.add_row(*row)

    console.print(table)


@label_app.command(name="add")
def command_add_labels_to_active_experiment(
    ctx: typer.Context,
    labels: list[str] = typer.Argument(..., help="A list of labels to add."),
):
    """Adds labels to the active experiment."""
    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.add_labels_to_active_experiment(labels)
    handle_result(res.is_success, res.message)


@label_app.command(name="assign")
def command_assign_labels(ctx: typer.Context):
    """No arguments. Assign or unassign labels to the active experiment using the default editor."""
    manager: ExperimentManager = resolve_manager(ctx)

    # gets the current label map of the active experiment
    res_map = manager.get_active_experiment_label_map()
    if not res_map.is_success:
        handle_result(False, res_map.message)
        return

    # edits the label status
    edited_map = edit_label_map_via_editor(ctx=manager.ctx, label_map=res_map.label_map)

    # updates the labels
    selected_labels = [name for name, active in edited_map.items() if active]
    res = manager.update_active_experiment_labels(selected_labels)
    handle_result(res.is_success, res.message)


@label_app.command(name="remove")
def command_remove_labels(
    ctx: typer.Context,
    labels: list[str] = typer.Argument(..., help="A list of label names to remove."),
):
    """Remove labels from the global label list and all experiments."""
    confirm = typer.confirm(
        f"Remove labels '{labels}' from the global list and all experiments?"
    )
    if not confirm:
        raise typer.Abort()

    manager: ExperimentManager = resolve_manager(ctx)
    res = manager.remove_global_labels(labels)
    handle_result(res.is_success, res.message)
