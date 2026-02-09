from simple_experiment_manager.io.handlers import ExperimentDataIO
from simple_experiment_manager.schemas import requests as req_schemas
from simple_experiment_manager.schemas import responses as res_schemas
from simple_experiment_manager.schemas.contexts import ExperimentContext


def add_global_label(
    request: req_schemas.RequestAddGlobalLabel, context: ExperimentContext
) -> res_schemas.ResponseAddGlobalLabel:
    """Adds a label to the global label set."""
    io = ExperimentDataIO(context)

    try:
        index = io.load_index()
        target_label = request.label_name

        # check the label name existence
        if target_label in index.global_labels:
            return res_schemas.ResponseAddGlobalLabel(
                is_success=True,
                message=f"Label '{target_label}' already exists in the global label set.",
                current_index=index,
            )

        # add the label name to the global label set
        index.global_labels.add(target_label)

        # save the updated index
        io.save_index(index)

        return res_schemas.ResponseAddGlobalLabel(
            is_success=True,
            message=f"Label '{target_label}' has been added to the global label set.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseAddGlobalLabel(is_success=False, message=str(e))


def remove_global_label(
    request: req_schemas.RequestRemoveGlobalLabel, context: ExperimentContext
) -> res_schemas.ResponseRemoveGlobalLabel:
    """Removes a label from the global list and cleans it up from all experiments."""
    io = ExperimentDataIO(context)

    try:
        index = io.load_index()
        target_label = request.label_name

        # validate existence
        if target_label not in index.global_labels:
            return res_schemas.ResponseRemoveGlobalLabel(
                is_success=False,
                message=f"Label '{target_label}' does not exist in global labels.",
            )

        # remove the label from global label set
        index.global_labels.discard(target_label)

        # remove the label from all experiments
        for experiment_meta in index.experiments.values():
            experiment_meta.labels.discard(target_label)

        # save the updated index
        io.save_index(index)

        return res_schemas.ResponseRemoveGlobalLabel(
            is_success=True,
            message=f"Label {target_label} has been removed globally and from all experiments.",
            current_index=index,
        )

    except Exception as e:
        return res_schemas.ResponseRemoveGlobalLabel(is_success=False, message=str(e))


def update_experiment_labels(
    request: req_schemas.RequestUpdateExperimentLabels, context: ExperimentContext
) -> res_schemas.ResponseUpdateExperimentLabels:
    """Updates labels for a experiment after validating they exist in global labels."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()

        # validate the experiment existence
        if request.experiment_name not in index.experiments:
            return res_schemas.ResponseUpdateExperimentLabels(
                is_success=False, message=f"Experiment '{request.experiment_name}' not found."
            )

        # validate the subset relationship (request.labels ⊆ index.global_labels)
        if not (request.labels <= index.global_labels):
            invalid_labels = request.labels - index.global_labels
            return res_schemas.ResponseUpdateExperimentLabels(
                is_success=False,
                message=f"Labels must be a subset of global labels. Invalid: {invalid_labels}",
            )

        # update and save index
        index.experiments[request.experiment_name].labels = request.labels
        io.save_index(index)

        return res_schemas.ResponseUpdateExperimentLabels(
            is_success=True,
            message=f"Labels for '{request.experiment_name}' updated successfully.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseUpdateExperimentLabels(is_success=False, message=str(e))


def get_label_usage(
    request: req_schemas.RequestGetLabelUsage, context: ExperimentContext
) -> res_schemas.ResponseGetLabelUsage:
    """Calculates which labels are used by which experiments."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()
        # initialize the label dict
        usage = {label: set() for label in index.global_labels}

        # map experiment names by scanning each experiment meta data
        for experiment_name, meta in index.experiments.items():
            for label in meta.labels:
                if label in usage:
                    usage[label].add(experiment_name)

        return res_schemas.ResponseGetLabelUsage(
            is_success=True, message="Successfully calculated label usage.", usage=usage
        )
    except Exception as e:
        return res_schemas.ResponseGetLabelUsage(is_success=False, message=str(e))


def get_experiment_label_map(
    request: req_schemas.RequestGetExperimentLabelMap, context: ExperimentContext
) -> res_schemas.ResponseGetExperimentLabelMap:
    """Returns a dictionary of all global labels with booleans indicating if the experiment has them."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()

        # validate experiment existence
        if request.experiment_name not in index.experiments:
            return res_schemas.ResponseGetExperimentLabelMap(
                is_success=False, message=f"Experiment '{request.experiment_name}' not found."
            )

        # get current labels of the experiment
        experiment_labels = index.experiments[request.experiment_name].labels

        # Create the map: {global_label: is_used_by_experiment}
        label_map = {label: (label in experiment_labels) for label in index.global_labels}

        return res_schemas.ResponseGetExperimentLabelMap(
            is_success=True,
            message=f"Successfully retrieved label map for '{request.experiment_name}'.",
            label_map=label_map,
        )
    except Exception as e:
        return res_schemas.ResponseGetExperimentLabelMap(is_success=False, message=str(e))
