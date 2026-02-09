from simple_experiment_manager.io.handlers import ExperimentDataIO
from simple_experiment_manager.schemas import requests as req_schemas
from simple_experiment_manager.schemas import responses as res_schemas
from simple_experiment_manager.schemas.contexts import ExperimentContext


def get_index(
    request: req_schemas.RequestGetIndex, context: ExperimentContext
) -> res_schemas.ResponseGetIndex:
    """Gets the experiment index."""
    io = ExperimentDataIO(context)

    try:
        index = io.load_index()

        return res_schemas.ResponseGetIndex(
            is_success=True,
            message="Successfully obtained the experiment index.",
            current_index=index,
        )
    except Exception as e:
        return res_schemas.ResponseGetIndex(is_success=False, message=str(e))
