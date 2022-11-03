import json
import pandas as pd
from typing import Tuple
import click

from ml_project.data.make_dataset import (
    read_data,
    split_train_test_data,
    divide_df_to_sings_marks
)
from reports.utils.logger import logger
from ml_project.entities.train_pipeline_params import TrainingPipelineParams
from ml_project.features.build_features import (
    build_transformer,
    make_features
)
from ml_project.entities.train_pipeline_params import read_training_pipeline_params
from ml_project.models.model_fit_predict import (
    train_model,
    create_inference_pipeline,
    predict_model,
    evaluate_model,
    serialize_model
)

def train_pipeline(config_path: str):
    training_pipline_params = read_training_pipeline_params(config_path)

    # add handling mlflow
    return run_train_pipeline(training_pipline_params)

def run_train_pipeline(training_pipeline_params: TrainingPipelineParams) -> Tuple[str, str]:
    logger.info(f"__Start training :: params = {training_pipeline_params}")
    data_frame = read_data(training_pipeline_params.input_data_path)
    split_data_frame = divide_df_to_sings_marks(data_frame)
    X_train, X_test, y_train, y_test = split_train_test_data(
        split_data_frame, training_pipeline_params.split_params
    )

    logger.info(f"""Dataframe:\n
        X_train  y_train :: {X_train.shape} {y_train.shape} \
        X_test   y_test  :: {X_test.shape} {y_test.shape}"""
    )

    transformer = build_transformer(training_pipeline_params.feature_params)
    transformer.fit(X_train)
    # train_features = make_features(transformer, X_train)
    model = train_model(
        X_train, y_train, training_pipeline_params.train_params
    )

    inference_pipeline = create_inference_pipeline(model, transformer)

    y_pred = predict_model(
        inference_pipeline,
        X_test
    )

    metrics = evaluate_model(
        y_pred,
        y_test
    )

    with open(training_pipeline_params.metric_path, "w") as metric_file:
        json.dump(metrics, metric_file)
    logger.info(f"Metrics :: {metrics}")

    path_to_model = serialize_model(
        inference_pipeline, training_pipeline_params.output_model_path
    )
    return path_to_model, metrics


@click.command()
@click.argument("config_path", help='Enter path to config')
def main(config_path: str):
    train_pipeline(config_path)

    
if __name__ == "__main__":
    main()