from datetime import datetime
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field


class ExperimentMetadata(BaseModel):
    """Metadata for an individual experiment."""

    created_at: Annotated[
        datetime,
        Field(
            description="The datetime when the experiment is created.",
        ),
    ] = Field(default_factory=datetime.now)
    labels: Annotated[set[str], Field(description="Labels that the experiment has.")] = (
        Field(default_factory=set)
    )
    config_path: Annotated[Path, Field(description="Path to the config file.")]


class ExperimentIndex(BaseModel):
    """The master index for all experiments managed by the library."""

    active_experiment: Annotated[
        str | None, Field(description="The active experiment name.")
    ] = None
    global_labels: Annotated[
        set[str], Field(description="Available experiment labels　to group experiments.")
    ] = Field(default_factory=set)
    experiments: Annotated[
        dict[str, ExperimentMetadata],
        Field(description="A dictionary of experiment metadata"),
    ] = Field(default_factory=dict)
