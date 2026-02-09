from typing import Final

import typer
from rich.console import Console

from simple_experiment_manager.manager import ExperimentManager

console = Console()

MANAGER_ATTR: Final[str] = "experiment_manager"


def handle_result(
    is_success: bool, message: str, terminate_on_error: bool = True
) -> None:
    """Handles the result message display by the use of `Rich`.

    Args:
        is_success: If the operation completed successfully.
        message: The message to display in console.
        terminate_on_error: If `True`, the failure operation will be terminated. Defaults to `True`.
    """
    if is_success:
        console.print(f"[green]Success:[/green] {message}")
    else:
        console.print(f"[red]Error:[/red] {message}")
        if terminate_on_error:
            raise typer.Exit(code=1)


def initialize_context(ctx: typer.Context) -> None:
    """Ensures that the Typer context object is initialized."""
    if ctx.obj is None:
        ctx.obj = {}


def resolve_manager(ctx: typer.Context) -> ExperimentManager:
    """Resolves the `ExperimentManager` instance from the `typer.Context`.

    `ctx.obj` must satisfy one of the following　conditions:
    - It is a `ExperimentManager` instance.
    - It is a dictionary containing the 'experiment_manager' key mapped to a `ExperimentManager` instance.
    - It is an object with a 'experiment_manager' attribute that is a `ExperimentManager` instance.

    Args:
        ctx: The `typer.Context` instance.

    Returns:
        The resolved `ExperimentManager` instance.

    Raises:
        RuntimeError: If `typer.Context` does not meet any of the conditions above.
    """
    obj = ctx.obj

    if isinstance(obj, ExperimentManager):
        return obj

    if isinstance(obj, dict):
        manager = obj.get(MANAGER_ATTR)
        if isinstance(manager, ExperimentManager):
            return manager

    manager = getattr(obj, MANAGER_ATTR, None)
    if isinstance(manager, ExperimentManager):
        return manager

    raise RuntimeError(
        f"Could not resolve ExperimentManager from {type(obj).__name__}."
        f"Please ensure `ctx.obj` or `ctx.obj.{MANAGER_ATTR}` is a `ExperimentManager` instance."
    )
