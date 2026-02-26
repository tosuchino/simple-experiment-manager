from simple_experiment_manager.io.handlers import ExperimentDataIO
from simple_experiment_manager.schemas import requests as req_schemas
from simple_experiment_manager.schemas import responses as res_schemas
from simple_experiment_manager.schemas.contexts import ExperimentContext
from simple_experiment_manager.schemas.validators import ensure_unique_list


def add_labels_to_experiment(
    request: req_schemas.RequestAddLabelsToExperiment, context: ExperimentContext
) -> res_schemas.ResponseAddLabelsToExperiment:
    """Adds labels to a specific experiment and ensures they are registered in global labels."""
    io = ExperimentDataIO(context)

    try:
        index = io.load_index()
        experiment_name = request.experiment_name

        # validate the experiment existence
        if experiment_name not in index.experiments:
            return res_schemas.ResponseAddLabelsToExperiment(
                is_success=False, message=f"Experiment '{experiment_name}' not found."
            )

        # early return if input labels are empty
        if not request.labels:
            return res_schemas.ResponseAddLabelsToExperiment(
                is_success=True,
                message="No labels provided; nothing changed.",
                current_index=index,
            )

        current_experiment_labels = index.experiments[experiment_name].labels
        current_global_labels = index.global_labels
        new_labels = request.labels

        # update the experiment label list and global label list
        index.experiments[experiment_name].labels = ensure_unique_list(
            current_experiment_labels + new_labels
        )
        index.global_labels = ensure_unique_list(current_global_labels + new_labels)

        # save the updated index
        io.save_index(index)

        return res_schemas.ResponseAddLabelsToExperiment(
            is_success=True,
            message=f"Added labels {new_labels} to the experiment '{experiment_name}'.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseAddLabelsToExperiment(
            is_success=False, message=str(e)
        )


def remove_global_labels(
    request: req_schemas.RequestRemoveGlobalLabels, context: ExperimentContext
) -> res_schemas.ResponseRemoveGlobalLabels:
    """Removes labels from the global list and cleans them up from all experiments."""
    io = ExperimentDataIO(context)

    try:
        index = io.load_index()
        target_labels = request.labels
        target_labels_set = set(request.labels)

        # validate existence
        if not target_labels_set & set(index.global_labels):
            return res_schemas.ResponseRemoveGlobalLabels(
                is_success=False,
                message=f"No labels to remove from the global labels: '{target_labels}'.",
            )

        # remove the labels from global label list
        index.global_labels = [
            label for label in index.global_labels if label not in target_labels_set
        ]

        # remove the labels from all experiments
        for experiment_meta in index.experiments.values():
            experiment_meta.labels = [
                label
                for label in experiment_meta.labels
                if label not in target_labels_set
            ]

        # save the updated index
        io.save_index(index)

        return res_schemas.ResponseRemoveGlobalLabels(
            is_success=True,
            message=f"Labels {target_labels} have been removed globally and from all experiments.",
            current_index=index,
        )

    except Exception as e:
        return res_schemas.ResponseRemoveGlobalLabels(is_success=False, message=str(e))


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
                is_success=False,
                message=f"Experiment '{request.experiment_name}' not found.",
            )

        # validate the subset relationship (request.labels ⊆ index.global_labels)
        req_labels_set = set(request.labels)
        global_labels_set = set(index.global_labels)
        if not req_labels_set <= global_labels_set:
            unknown_labels_set = req_labels_set - global_labels_set
            return res_schemas.ResponseUpdateExperimentLabels(
                is_success=False,
                message=f"Unknown labels found: {unknown_labels_set}. Please add them first.",
            )

        # update and save index
        index.experiments[request.experiment_name].labels = ensure_unique_list(
            request.labels
        )
        io.save_index(index)

        return res_schemas.ResponseUpdateExperimentLabels(
            is_success=True,
            message=f"Labels for '{request.experiment_name}' updated successfully.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseUpdateExperimentLabels(
            is_success=False, message=str(e)
        )


def get_label_usage(
    request: req_schemas.RequestGetLabelUsage, context: ExperimentContext
) -> res_schemas.ResponseGetLabelUsage:
    """Retrieve a mapping of labels to the experiments that use them."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()
        # initialize the label dict
        usage: dict[str, list[str]] = {label: list() for label in index.global_labels}

        # map experiment names by scanning each experiment meta data
        for experiment_name, meta in index.experiments.items():
            for label in meta.labels:
                if label in usage:
                    usage[label].append(experiment_name)

        return res_schemas.ResponseGetLabelUsage(
            is_success=True, message="Successfully retrieved label usage.", usage=usage
        )
    except Exception as e:
        return res_schemas.ResponseGetLabelUsage(is_success=False, message=str(e))


def get_experiment_label_map(
    request: req_schemas.RequestGetExperimentLabelMap, context: ExperimentContext
) -> res_schemas.ResponseGetExperimentLabelMap:
    """Returns a dictionary of all global labels with booleans indicating if the specified experiment has them."""
    io = ExperimentDataIO(context)
    try:
        index = io.load_index()

        # validate experiment existence
        if request.experiment_name not in index.experiments:
            return res_schemas.ResponseGetExperimentLabelMap(
                is_success=False,
                message=f"Experiment '{request.experiment_name}' not found.",
            )

        # get current labels of the experiment
        experiment_labels = index.experiments[request.experiment_name].labels

        # Create the map: {global_label: is_used_by_experiment}
        label_map = {
            label: (label in experiment_labels) for label in index.global_labels
        }

        return res_schemas.ResponseGetExperimentLabelMap(
            is_success=True,
            message=f"Successfully retrieved label map for '{request.experiment_name}'.",
            label_map=label_map,
        )
    except Exception as e:
        return res_schemas.ResponseGetExperimentLabelMap(
            is_success=False, message=str(e)
        )
