from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from simple_experiment_manager.schemas.contexts import ConfigClass
from simple_experiment_manager.schemas.validators import validate_safe_name


# experiments
class RequestCreateExperiment(BaseModel):
    # model configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # fields
    experiment_name: Annotated[str, Field(description="The experiment name to create.")]
    config: Annotated[
        BaseModel | ConfigClass | None,
        Field(
            description="The actual configuration instance. If None, the default config is used."
        ),
    ] = Field(default=None)

    @field_validator("experiment_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_safe_name(v)


class RequestSetActiveExperiment(BaseModel):
    experiment_name: Annotated[
        str, Field(description="The name of the experiment to set as active.")
    ]


class RequestDeleteExperiment(BaseModel):
    experiment_name: Annotated[
        str, Field(description="The name of the experiment to delete.")
    ]


class RequestCopyExperiment(BaseModel):
    src_experiment_name: Annotated[
        str, Field(description="The name of the source experiment to copy from.")
    ]
    dst_experiment_name: Annotated[
        str, Field(description="The name of the destination experiment to copy to.")
    ]

    @field_validator("dst_experiment_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_safe_name(v)


class RequestUpdateExperimentConfig(BaseModel):
    # model configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # fields
    experiment_name: Annotated[
        str, Field(description="The name of the experiment to update.")
    ]
    config: Annotated[
        BaseModel | ConfigClass, Field(description="The new configuration instance.")
    ]


class RequestRenameExperiment(BaseModel):
    old_experiment_name: Annotated[
        str, Field(description="The current name of the experiment to rename.")
    ]
    new_experiment_name: Annotated[
        str, Field(description="The new name of the experiment to rename.")
    ]

    @field_validator("new_experiment_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_safe_name(v)


class RequestGetExperimentConfig(BaseModel):
    experiment_name: Annotated[
        str,
        Field(
            description="The name of the experiment whose configuration is to be retrieved."
        ),
    ]


# labels
class RequestAddLabelsToExperiment(BaseModel):
    experiment_name: Annotated[
        str,
        Field(description="The name of the experiment to add labels to."),
    ]
    labels: Annotated[list[str], Field(description="A list of label names to add.")]


class RequestRemoveGlobalLabels(BaseModel):
    labels: Annotated[
        list[str],
        Field(
            description="A list of label names to remove globally and from all experiments."
        ),
    ]


class RequestUpdateExperimentLabels(BaseModel):
    experiment_name: Annotated[
        str, Field(description="The name of the experiment to update.")
    ]
    labels: Annotated[
        list[str], Field(description="A list of labels to assign to the experiment.")
    ]


class RequestGetLabelUsage(BaseModel):
    pass


class RequestGetExperimentLabelMap(BaseModel):
    experiment_name: Annotated[
        str, Field(description="The name of the experiment to check label usage.")
    ]


# index
class RequestGetIndex(BaseModel):
    pass
