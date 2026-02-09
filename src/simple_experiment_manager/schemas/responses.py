from typing import Annotated, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from simple_experiment_manager.schemas.contexts import ConfigClass
from simple_experiment_manager.schemas.index import ExperimentIndex


class BaseResponse(BaseModel):
    is_success: Annotated[
        bool, Field(description="Whether the operation completed successfully.")
    ]
    message: Annotated[str, Field(description="A message for the results.")] = ""
    current_index: Annotated[
        ExperimentIndex | None,
        Field(description="A current `ExperimentIndex` instance or `None`."),
    ] = None


# experiment
class ResponseCreateExperiment(BaseResponse):
    pass


class ResponseSetActiveExperiment(BaseResponse):
    pass


class ResponseDeleteExperiment(BaseResponse):
    pass


class ResponseCopyExperiment(BaseResponse):
    pass


class ResponseUpdateExperimentConfig(BaseResponse):
    pass


class ResponseRenameExperiment(BaseResponse):
    pass


class ResponseGetExperimentConfig(BaseResponse):
    # model configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # fields
    config: Annotated[
        BaseModel | ConfigClass | None,
        Field(description="The configuration instance of the experiment."),
    ] = Field(default=None)


# label
class ResponseAddGlobalLabel(BaseResponse):
    pass


class ResponseRemoveGlobalLabel(BaseResponse):
    pass


class ResponseUpdateExperimentLabels(BaseResponse):
    pass


class ResponseGetLabelUsage(BaseResponse):
    usage: Annotated[
        dict[str, set[str]],
        Field(
            description="A dictionary of labels whose values are sets of experiment names."
        ),
    ] = Field(default_factory=dict)


class ResponseGetExperimentLabelMap(BaseResponse):
    label_map: Annotated[
        dict[str, bool],
        Field(
            description="A mapping of all global labels to booleans indicating their assignment to the experiment."
        ),
    ] = Field(default_factory=dict)


# index
class ResponseGetIndex(BaseResponse):
    pass


ExperimentManagerResponse: TypeAlias = (
    ResponseCreateExperiment
    | ResponseSetActiveExperiment
    | ResponseDeleteExperiment
    | ResponseCopyExperiment
    | ResponseUpdateExperimentConfig
    | ResponseRenameExperiment
    | ResponseGetExperimentConfig
    | ResponseGetExperimentLabelMap
    | ResponseAddGlobalLabel
    | ResponseRemoveGlobalLabel
    | ResponseUpdateExperimentLabels
    | ResponseGetLabelUsage
    | ResponseGetIndex
)
