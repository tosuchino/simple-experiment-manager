from pathlib import Path

from pydantic import BaseModel

from simple_experiment_manager.api import experiment as api_experiment
from simple_experiment_manager.api import index as api_index
from simple_experiment_manager.api import label as api_label
from simple_experiment_manager.schemas import requests as req_schemas
from simple_experiment_manager.schemas import responses as res_schemas
from simple_experiment_manager.schemas.contexts import ConfigClass, ExperimentContext
from simple_experiment_manager.schemas.index import ExperimentIndex, ExperimentMetadata


class ExperimentManager:
    """The main API for managing experiments and their configurations.

    This class orchestrates experiment creation, indexing, and label management
    by delegating business logic to specialized API functions.
    """

    def __init__(self, ctx: ExperimentContext) -> None:
        """Initializes the manager with a experiment context."""
        self.ctx: ExperimentContext = ctx
        self._index: ExperimentIndex | None = None
        self.refresh()

    def _update_state(self, response: res_schemas.ExperimentManagerResponse) -> None:
        """Updates the internal state with the given response."""
        if response.is_success and response.current_index:
            self._index = response.current_index

    def refresh(self) -> None:
        """Gets the current index and updates the internal state."""
        req = req_schemas.RequestGetIndex()
        res = api_index.get_index(request=req, context=self.ctx)
        self._update_state(res)

    def create_experiment(
        self, name: str, config: BaseModel | ConfigClass | None = None
    ) -> res_schemas.ResponseCreateExperiment:
        """Creates a new experiment directory and initializes its configuration file.

        Args:
            name: A unique name for the experiment. Used as the experiment key and directory name.
            config: An instance of the configuration whith must match the type of ctx.default_config.
                If None, default_config is used. Defaults to None.

        Returns:
            A `ResponseCreateExperiment` instance.
        """
        req = req_schemas.RequestCreateExperiment(experiment_name=name, config=config)
        res = api_experiment.create_experiment(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def set_active_experiment(
        self, name: str
    ) -> res_schemas.ResponseSetActiveExperiment:
        """Switches the active experiment.

        Args:
           name: A experiment name to be active.

        Returns:
            A `ResponseSetActiveExperiment` instance.
        """
        req = req_schemas.RequestSetActiveExperiment(experiment_name=name)
        res = api_experiment.set_active_experiment(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def delete_experiment(self, name: str) -> res_schemas.ResponseDeleteExperiment:
        """Deletes the experiment directory and removes it from the index.

        If the deleted experiment is set to be active, `active_experiment` in the index is set to `None`.

        Args:
           name: A experiment name to delete.

        Returns:
            A `ResponseDeleteExperiment` instance.
        """
        req = req_schemas.RequestDeleteExperiment(experiment_name=name)
        res = api_experiment.delete_experiment(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def copy_experiment(
        self, src_name: str, dst_name: str
    ) -> res_schemas.ResponseCopyExperiment:
        """Creates a new experiment by copying the existing experiment.

        Args:
            src_name: The experiment name to copy from.
            dst_name: The experiment name to copy to.

        Returns:
            A `ResponseCopyExperiment` instance.
        """
        req = req_schemas.RequestCopyExperiment(
            src_experiment_name=src_name, dst_experiment_name=dst_name
        )
        res = api_experiment.copy_experiment(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def update_experiment_config(
        self, name: str, config: BaseModel | ConfigClass
    ) -> res_schemas.ResponseUpdateExperimentConfig:
        """Updates the configuration for a experiment.

        Args:
            name: The name of the experiment whose configuration will be updated.
            config: The new experiment configuration matching the type of context's `default_config`.

        Returns:
            A `ResponseUpdateExperimentConfig` instance.
        """
        req = req_schemas.RequestUpdateExperimentConfig(
            experiment_name=name, config=config
        )
        res = api_experiment.update_experiment_config(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def update_active_experiment_config(
        self, config: BaseModel | ConfigClass
    ) -> res_schemas.ResponseUpdateExperimentConfig:
        """Updates the configuration for the currently active experiment.

        Args:
            config: The new experiment configuration matching the type of context's `default_config`.

        Returns:
            A `ResponseUpdateExperimentConfig` instance.
        """
        if name := self.active_experiment:
            return self.update_experiment_config(name=name, config=config)
        return res_schemas.ResponseUpdateExperimentConfig(
            is_success=False, message="No active experiment set."
        )

    def rename_experiment(
        self, old_name: str, new_name: str
    ) -> res_schemas.ResponseRenameExperiment:
        """Renames the experiment name.

        Args:
            old_name: The old experiment name.
            new_name: The new experiment name.

        Returns:
            A `ResponseRenameExperiment` instance.
        """
        req = req_schemas.RequestRenameExperiment(
            old_experiment_name=old_name, new_experiment_name=new_name
        )
        res = api_experiment.rename_experiment(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def rename_active_experiment(
        self, new_name: str
    ) -> res_schemas.ResponseRenameExperiment:
        """Renames the currently active experiment name.

        Args:
            new_name: The new experiment name.

        Returns:
            A `ResponseRenameExperiment` instance.

        """
        if old_name := self.active_experiment:
            return self.rename_experiment(old_name=old_name, new_name=new_name)
        return res_schemas.ResponseRenameExperiment(
            is_success=False, message="No active experiment set."
        )

    def get_experiment_config(
        self, name: str
    ) -> res_schemas.ResponseGetExperimentConfig:
        """Retrieves the configuration for a experiment.

        Args:
            name: The experiment name whose configuration is to be retrieved.

        Returns:
            A `ResponseGetExperimentConfig` instance.
        """
        req = req_schemas.RequestGetExperimentConfig(experiment_name=name)
        res = api_experiment.get_experiment_config(request=req, context=self.ctx)
        return res

    def get_active_experiment_config(self) -> res_schemas.ResponseGetExperimentConfig:
        """Retrieves the configuration for the currently active experiment.

        Returns:
            A `ResponseGetExperimentConfig` instance.
        """
        if name := self.active_experiment:
            return self.get_experiment_config(name=name)
        return res_schemas.ResponseGetExperimentConfig(
            is_success=False, message="No active experiment set."
        )

    def add_labels_to_experiment(
        self, experiment_name: str, labels: list[str]
    ) -> res_schemas.ResponseAddLabelsToExperiment:
        """Adds labels to the experiment and ensures they are registered in the global label list.

        Args:
           experiment_name: The experiment name to add labels to.
           labels: A list of label names to add.

        Returns:
            A `ResponseAddLabelsToExperiment` instance.
        """
        req = req_schemas.RequestAddLabelsToExperiment(
            experiment_name=experiment_name, labels=labels
        )
        res = api_label.add_labels_to_experiment(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def add_labels_to_active_experiment(
        self, labels: list[str]
    ) -> res_schemas.ResponseAddLabelsToExperiment:
        """Adds labels to the active experiment and ensures they are registered in the global label list.

        Args:
           labels: A list of label names to add.

        Returns:
            A `ResponseAddLabelsToExperiment` instance.
        """
        if experiment_name := self.active_experiment:
            return self.add_labels_to_experiment(
                experiment_name=experiment_name, labels=labels
            )
        return res_schemas.ResponseAddLabelsToExperiment(
            is_success=False, message="No active experiment set."
        )

    def remove_global_labels(
        self, labels: list[str]
    ) -> res_schemas.ResponseRemoveGlobalLabels:
        """Removes multiple labels from the global label list and from all the experiments.

        Args:
           labels: A list of label names to remove from the global label list.

        Returns:
            A `ResponseRemoveGlobalLabels` instance.
        """
        req = req_schemas.RequestRemoveGlobalLabels(labels=labels)
        res = api_label.remove_global_labels(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def update_experiment_labels(
        self, experiment_name: str, labels: list[str]
    ) -> res_schemas.ResponseUpdateExperimentLabels:
        """Updates labels for a experiment.

        Args:
           experiment_name: The name of the experiment whose labels will be updated.
           labels: A list of label names to assign. All labels must already exist in the global label　list.

        Returns:
            A `ResponseUpdateExperimentLabels` instance.
        """
        req = req_schemas.RequestUpdateExperimentLabels(
            experiment_name=experiment_name, labels=labels
        )
        res = api_label.update_experiment_labels(request=req, context=self.ctx)
        self._update_state(res)
        return res

    def update_active_experiment_labels(
        self, labels: list[str]
    ) -> res_schemas.ResponseUpdateExperimentLabels:
        """Updates labels for the currently active experiment.

        Args:
            labels: A list of label names to assign. All labels must already exist in the global label　list.

        Returns:
            A `ResponseUpdateExperimentLabels` instance.
        """
        if experiment_name := self.active_experiment:
            return self.update_experiment_labels(
                experiment_name=experiment_name, labels=labels
            )
        return res_schemas.ResponseUpdateExperimentLabels(
            is_success=False, message="No active experiment set."
        )

    def get_label_usage(self) -> res_schemas.ResponseGetLabelUsage:
        """Gets the label usage, providing a mapping of the labels to the sets of experiment names that use them.

        Returns:
            A `ResponseGetLabelUsage` instance.
        """
        req = req_schemas.RequestGetLabelUsage()
        res = api_label.get_label_usage(request=req, context=self.ctx)
        return res

    def get_experiment_label_map(
        self, name: str
    ) -> res_schemas.ResponseGetExperimentLabelMap:
        """Gets a map of all global labels and whether they are assigned to the specified experiment.

        Args:
            name: The experiment name to acquire the label map.

        Returns:
            A `ResponseGetExperimentLabelMap` instance.
        """
        req = req_schemas.RequestGetExperimentLabelMap(experiment_name=name)
        return api_label.get_experiment_label_map(request=req, context=self.ctx)

    def get_active_experiment_label_map(
        self,
    ) -> res_schemas.ResponseGetExperimentLabelMap:
        """Gets a map of all global labels and whether they are assigned to the active experiment.

        Returns:
            A `ResponseGetExperimentLabelMap` instance.
        """
        if name := self.active_experiment:
            return self.get_experiment_label_map(name=name)
        return res_schemas.ResponseGetExperimentLabelMap(
            is_success=False, message="No active experiment set."
        )

    @property
    def experiment_root(self) -> Path:
        """Provides the experiment root path."""
        return self.ctx.experiment_root

    @property
    def experiment_index_file(self) -> Path:
        """Provides the path to the experiment index file."""
        return self.ctx.experiment_index_file

    def get_experiment_dir(self, name: str) -> Path:
        """Gets the directory path for a specific experiment."""
        return self.ctx.get_experiment_dir(name)

    def get_experiment_config_file(self, name: str) -> Path:
        """Gets the configuration file path for a specific experiment."""
        return self.ctx.get_config_file(name)

    @property
    def active_experiment_dir(self) -> Path | None:
        """Provides the directory path for the active experiment."""
        if name := self.active_experiment:
            return self.get_experiment_dir(name)
        return None

    @property
    def active_experiment_config_file(self) -> Path | None:
        """Provides the configuration file path for the active experiment."""
        if name := self.active_experiment:
            return self.get_experiment_config_file(name)
        return None

    @property
    def index(self) -> ExperimentIndex | None:
        """Provides the current `ExperimentIndex` instance. Returns `None` if not yet loaded."""
        return self._index

    @property
    def global_labels(self) -> list[str]:
        """Gets the list of labels defined at the global level."""
        return self.index.global_labels if self.index else list()

    @property
    def active_experiment(self) -> str | None:
        """Gets the name of the currently active experiment, if it is set."""
        return self.index.active_experiment if self.index else None

    @property
    def active_experiment_metadata(self) -> ExperimentMetadata | None:
        """Gets the metadata for the active experiment."""
        if (idx := self.index) and (name := self.active_experiment):
            return idx.experiments.get(name)
        return None

    @property
    def experiments(self) -> list[str]:
        """Gets the set of all registered experiment names."""
        return list(self.index.experiments.keys()) if self.index else list()
