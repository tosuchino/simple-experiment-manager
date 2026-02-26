from typing import Any

from pydantic import BaseModel

from simple_experiment_manager.io.handlers import ExperimentDataIO
from simple_experiment_manager.schemas import requests as req_schemas
from simple_experiment_manager.schemas import responses as res_schemas
from simple_experiment_manager.schemas.contexts import ConfigClass, ExperimentContext
from simple_experiment_manager.schemas.index import ExperimentIndex, ExperimentMetadata


def create_experiment(
    request: req_schemas.RequestCreateExperiment, context: ExperimentContext
) -> res_schemas.ResponseCreateExperiment:
    io = ExperimentDataIO(context)

    try:
        actual_config = request.config
        if not actual_config:
            default_config = context.default_config
            if isinstance(default_config, BaseModel):
                actual_config = default_config.model_copy(deep=True)
            else:
                actual_config = ConfigClass(**default_config.to_dict())
        updated_index = _create_experiment_core(
            experiment_name=request.experiment_name,
            config=actual_config,
            context=context,
            io=io,
        )

        return res_schemas.ResponseCreateExperiment(
            is_success=True,
            message=f"Experiment '{request.experiment_name}' created.",
            current_index=updated_index,
        )

    except Exception as e:
        return res_schemas.ResponseCreateExperiment(is_success=False, message=str(e))


def set_active_experiment(
    request: req_schemas.RequestSetActiveExperiment, context: ExperimentContext
) -> res_schemas.ResponseSetActiveExperiment:
    """Sets the specified experiment as the active experiment in the index."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()

        # validate the experiment existence
        if request.experiment_name not in index.experiments:
            return res_schemas.ResponseSetActiveExperiment(
                is_success=False,
                message=f"Experiment '{request.experiment_name}' does not exist.",
            )

        # update the active experiment
        index.active_experiment = request.experiment_name
        io.save_index(index)

        return res_schemas.ResponseSetActiveExperiment(
            is_success=True,
            message=f"Experiment '{request.experiment_name}' is now active.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseSetActiveExperiment(is_success=False, message=str(e))


def delete_experiment(
    request: req_schemas.RequestDeleteExperiment, context: ExperimentContext
) -> res_schemas.ResponseDeleteExperiment:
    """Permanently deletes the experiment directory and its metadata from the index."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()

        # validate experiment existence
        if request.experiment_name not in index.experiments:
            return res_schemas.ResponseDeleteExperiment(
                is_success=False,
                message=f"Experiment '{request.experiment_name}' does not exist.",
            )

        # delete the experiment directory
        io.delete_experiment_data(request.experiment_name)

        # remove the experiment from the index
        del index.experiments[request.experiment_name]

        # reset the active experiment if it is removed
        if index.active_experiment == request.experiment_name:
            index.active_experiment = None

        io.save_index(index)
        return res_schemas.ResponseDeleteExperiment(
            is_success=True,
            message=f"Experiment '{request.experiment_name}' deleted.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseDeleteExperiment(is_success=False, message=str(e))


def copy_experiment(
    request: req_schemas.RequestCopyExperiment, context: ExperimentContext
) -> res_schemas.ResponseCopyExperiment:
    """Creates a new experiment by copying another existing experiment config."""
    io = ExperimentDataIO(context)
    try:
        current_index = io.load_index()
        src_config = io.load_config(request.src_experiment_name)
        src_labels = current_index.experiments[request.src_experiment_name].labels
        updated_index = _create_experiment_core(
            experiment_name=request.dst_experiment_name,
            config=src_config,
            context=context,
            io=io,
            labels=src_labels,
        )
        return res_schemas.ResponseCopyExperiment(
            is_success=True,
            message=f"Copied from '{request.src_experiment_name}' to '{request.dst_experiment_name}'.",
            current_index=updated_index,
        )
    except Exception as e:
        return res_schemas.ResponseCopyExperiment(is_success=False, message=str(e))


def update_experiment_config(
    request: req_schemas.RequestUpdateExperimentConfig, context: ExperimentContext
) -> res_schemas.ResponseUpdateExperimentConfig:
    """Updates the configuration file of an existing experiment."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()

        # validate config type matching
        _validate_config_type(config=request.config, ctx=context)

        # validate experiment existence
        if request.experiment_name not in index.experiments:
            return res_schemas.ResponseUpdateExperimentConfig(
                is_success=False,
                message=f"Experiment '{request.experiment_name}' not found.",
            )

        # save the updated config
        io.save_config(experiment_name=request.experiment_name, config=request.config)

        return res_schemas.ResponseUpdateExperimentConfig(
            is_success=True,
            message=f"Configuration for '{request.experiment_name}' updated successfully.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseUpdateExperimentConfig(
            is_success=False, message=str(e)
        )


def rename_experiment(
    request: req_schemas.RequestRenameExperiment, context: ExperimentContext
) -> res_schemas.ResponseRenameExperiment:
    """Renames the experiment."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()

        # validate experiment existence
        if request.old_experiment_name not in index.experiments:
            return res_schemas.ResponseRenameExperiment(
                is_success=False,
                message=f"Experiment '{request.old_experiment_name}' not found.",
            )

        # rename the directory
        io.rename_experiment_dir(
            old_name=request.old_experiment_name, new_name=request.new_experiment_name
        )

        # pop the old metadata and update the relative config path
        metadata = index.experiments.pop(request.old_experiment_name)
        new_config_file = context.get_config_file(request.new_experiment_name)
        metadata.config_path = new_config_file.relative_to(context.experiment_root)

        # re-assign to the new key
        index.experiments[request.new_experiment_name] = metadata

        # update active experiment if necessary
        if index.active_experiment == request.old_experiment_name:
            index.active_experiment = request.new_experiment_name

        # save updated index
        io.save_index(index)

        return res_schemas.ResponseRenameExperiment(
            is_success=True,
            message=f"Experiment '{request.old_experiment_name}' renamed to '{request.new_experiment_name}'.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseRenameExperiment(is_success=False, message=str(e))


def get_experiment_config(
    request: req_schemas.RequestGetExperimentConfig, context: ExperimentContext
) -> res_schemas.ResponseGetExperimentConfig:
    """Retrieves the configuration instance for a specified experiment."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()
        config = io.load_config(request.experiment_name)
        return res_schemas.ResponseGetExperimentConfig(
            is_success=True,
            message=f"Configuration for experiment '{request.experiment_name}' successfully retrieved.",
            current_index=index,
            config=config,
        )
    except Exception as e:
        return res_schemas.ResponseGetExperimentConfig(is_success=False, message=str(e))


# helper functions


def _create_experiment_core(
    experiment_name: str,
    config: BaseModel | ConfigClass,
    context: ExperimentContext,
    io: ExperimentDataIO,
    labels: list[str] | None = None,
) -> ExperimentIndex:
    """Creates a experiment configuration and updates the experiment index after validation.

    This internal function handles shared logic for both `create` and `copy` operations.

    Args:
        experiment_name: The experiment name to create.
        config: The experiment configuration instance which matches the context's `default_config`.
        context: The experiment context.
        io: The experiment data IO handler.
        labels: A list of label names to add. If None, an empty list is used. Defaults to None.

    Returns:
        The updated `ExperimentIndex` instance.

    Raises:
        - FileExistsError: If a experiment directory having `experiment_name` already exists.
    """
    experiment_dir = context.get_experiment_dir(experiment_name)
    config_file = context.get_config_file(experiment_name)

    # validate config type
    _validate_config_type(config=config, ctx=context)

    # validate experiment existence
    if experiment_dir.exists():
        raise FileExistsError(f"Experiment name already exists: {experiment_name}")

    index = io.load_index()

    # save config file
    io.save_config(experiment_name=experiment_name, config=config)

    # update index file
    labels = labels if labels else list()
    index.experiments[experiment_name] = ExperimentMetadata(
        labels=labels, config_path=config_file.relative_to(context.experiment_root)
    )
    index.active_experiment = experiment_name
    io.save_index(index)

    return index


def _validate_config_type(config: Any, ctx: ExperimentContext) -> None:
    "Validates the type of `config` based on the experiment context."
    expected = ctx.default_config

    if isinstance(expected, BaseModel):
        if not isinstance(config, BaseModel):
            raise TypeError(
                f"Expected {type(expected).__name__}, got {type(config).__name__}"
            )
    elif isinstance(expected, ConfigClass):
        if not isinstance(config, ConfigClass):
            raise TypeError(f"Expected `ConfigClass`, got {type(config).__name__}")
