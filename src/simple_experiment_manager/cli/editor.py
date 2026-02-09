from io import StringIO
from typing import Any

import typer
from pydantic import BaseModel, ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from simple_experiment_manager.schemas.contexts import ConfigClass, ExperimentContext


def build_template_dict_from_config_class(
    instance: BaseModel | ConfigClass,
) -> CommentedMap:
    """Given a Pydantic model instance, a CommentedMap is recursively built."""
    data = CommentedMap()

    if isinstance(instance, ConfigClass):
        for name, value in instance.to_dict(mode="json").items():
            data[name] = value
        return data

    model_cls = type(instance)
    current_values = instance.model_dump()

    for name, field in model_cls.model_fields.items():
        value = current_values.get(name)
        field_type = field.annotation

        # Check if a field is nested
        if isinstance(value, dict) and field_type and issubclass(field_type, BaseModel):
            nested_instance = getattr(instance, name)
            data[name] = build_template_dict_from_config_class(nested_instance)
        else:
            data[name] = value

        # Field description
        if field.description:
            data.yaml_set_comment_before_after_key(name, before=field.description)

    return data


def edit_config_via_editor(
    ctx: ExperimentContext, data: CommentedMap
) -> BaseModel | ConfigClass:
    """Runs the default editor until valid data are input."""
    # generate yaml string
    current_yaml_text = generate_yaml_string(ctx=ctx, data=data)

    # runs the editor
    yaml = YAML(typ="safe")

    error_header = ""
    while True:
        instruction = (
            "# --- Experiment Configuration ---\n"
            "# Save and close the editor to apply changes.\n"
        )
        full_content = instruction + error_header + current_yaml_text

        edited_text = typer.edit(full_content, extension=".yaml")

        if edited_text is None:
            typer.echo("Operation cancelled.")
            raise typer.Abort()

        try:
            user_data = yaml.load(edited_text) or {}

            if isinstance(ctx.default_config, BaseModel):
                return ctx.default_config.__class__.model_validate(user_data)
            else:
                return ConfigClass(**user_data)

        except (ValidationError, Exception) as e:
            error_header = f"# [ERROR] {str(e)}\n\n"
            current_yaml_text = edited_text


def edit_label_map_via_editor(
    ctx: ExperimentContext, label_map: dict[str, bool]
) -> dict[str, bool]:
    """Run the default editor to update label usage status."""
    header = (
        "# --- Label Assignment ---\n"
        "# Set to 'true' to assign, or 'false' to unassign.\n\n"
    )
    yaml_text = generate_yaml_string(ctx, label_map, header=header)

    edited_text = typer.edit(yaml_text, extension=".yaml")
    if edited_text is None:
        typer.echo("Operation cancelled.")
        raise typer.Abort()

    yaml_safe = YAML(typ="safe")
    try:
        # load data as dict
        new_data = yaml_safe.load(edited_text)
        if not isinstance(new_data, dict):
            return {}

        # cast boolean value
        return {
            str(k): (isinstance(v, bool) and (v is True)) for k, v in new_data.items()
        }

    except Exception as e:
        typer.secho(f"Error parsing Label YAML: {e}", fg="red")
        raise typer.Abort()


def generate_yaml_string(ctx: ExperimentContext, data: Any, header: str = "") -> str:
    """Converts the given data into YAML strings."""
    yaml = YAML()
    yaml.indent(mapping=ctx.indent, sequence=ctx.indent + 2, offset=ctx.indent)

    stream = StringIO()
    if header:
        stream.write(header)
    yaml.dump(data, stream)
    return stream.getvalue()
