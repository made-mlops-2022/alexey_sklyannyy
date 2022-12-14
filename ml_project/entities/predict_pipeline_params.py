from dataclasses import dataclass
import yaml
from marshmallow_dataclass import class_schema

@dataclass()
class PredictingPipelineParams:
    input_data_path: str
    input_model_path: str
    output_data_path: str


PredictingPipelineParamsSchema = class_schema(PredictingPipelineParams)


def read_predicting_pipeline_params(config_path: str) -> PredictingPipelineParams:
    with open(config_path, "r") as input_stream:
        schema = PredictingPipelineParamsSchema()
        return schema.load(yaml.safe_load(input_stream))
