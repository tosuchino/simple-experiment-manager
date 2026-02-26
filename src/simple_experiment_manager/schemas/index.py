from datetime import datetime
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from simple_experiment_manager.schemas.validators import ensure_unique_list


class ExperimentMetadata(BaseModel):
    """Metadata for an individual experiment."""

    # model configuration
    model_config = ConfigDict(validate_assignment=True)

    # fields
    created_at: Annotated[
        datetime,
        Field(
            description="The datetime when the experiment is created.",
        ),
    ] = Field(default_factory=datetime.now)
    labels: Annotated[
        list[str], Field(description="Labels that the experiment has.")
    ] = Field(default_factory=list)
    config_path: Annotated[Path, Field(description="Path to the config file.")]

    @field_validator("labels", mode="after")
    @classmethod
    def validate_labels(cls, v: list[str]) -> list[str]:
        return ensure_unique_list(v)


class ExperimentIndex(BaseModel):
    """The master index for all experiments managed by the library."""

    # model configuration
    model_config = ConfigDict(validate_assignment=True)

    # fields
    active_experiment: Annotated[
        str | None, Field(description="The active experiment name.")
    ] = None
    global_labels: Annotated[
        list[str],
        Field(description="Available experiment labels　to group experiments."),
    ] = Field(default_factory=list)
    experiments: Annotated[
        dict[str, ExperimentMetadata],
        Field(description="A dictionary of experiment metadata"),
    ] = Field(default_factory=dict)

    @field_validator("global_labels", mode="after")
    @classmethod
    def validate_labels(cls, v: list[str]) -> list[str]:
        return ensure_unique_list(v)
