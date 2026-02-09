from pathlib import Path
from typing import Annotated

import pytest
from pydantic import BaseModel, Field

from simple_experiment_manager.manager import ExperimentManager
from simple_experiment_manager.schemas.contexts import ExperimentContext


# Dummy config
class DummyConfig(BaseModel):
    user_name: Annotated[str, Field(description="The user name.")] = Field(
        default="default"
    )
    debug_mode: Annotated[
        bool, Field(description="Whether the debug mode is active.")
    ] = Field(default=False)


@pytest.fixture
def dummy_ctx(tmp_path: Path) -> ExperimentContext:
    """Provides the dummy experiment context."""
    ctx = ExperimentContext(
        lib_name="dummy_lib", config_cls=DummyConfig, base_dir=tmp_path
    )
    return ctx


@pytest.fixture
def manager(dummy_ctx):
    """Provides the `ExperimentManager` instance."""
    return ExperimentManager(dummy_ctx)
