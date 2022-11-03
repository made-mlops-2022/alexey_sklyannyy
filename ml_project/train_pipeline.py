import json
import pandas as pd
from typing import Tuple
import click

import logging

from ml_project.data.make_dataset import (
    read_data,
    split_train_test_data,
    divide_df_to_sings_marks
)
from ml_project.entities.train_pipeline_params import TrainingPipelineParams
from ml_project.features.build_features import (
    build_transformer
)
from ml_project.entities.train_pipeline_params import read_training_pipeline_params
from ml_project.models.model_fit_predict import (
    train_model,
    create_inference_pipeline,
    predict_model,
    evaluate_model,
    serialize_model
)

# from ml_project.utils.log import setup_logger

# logging
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.FileHandler(log_file, mode="w")        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

logger = setup_logger("main", "handling_result.log")



def train_pipeline(config_path: str):
    training_pipline_params = read_training_pipeline_params(config_path)

    # add handling mlflow
    return run_train_pipeline(training_pipline_params)

def run_train_pipeline(training_pipeline_params: TrainingPipelineParams) -> Tuple[str, str]:
    logger.info(f"__Start training :: params = {training_pipeline_params}")
    data_frame = read_data(training_pipeline_params.input_data_path)
    split_data_frame = divide_df_to_sings_marks(data_frame)
    train_df, test_df, train_marks, test_marks = split_train_test_data(
        split_data_frame, training_pipeline_params.split_params
    )

    logger.info(f"""Dataframe:
        train_df  train_marks :: {train_df.shape} {train_marks.shape}
        test_df   test_marks  :: {test_df.shape} {test_marks.shape}"""
    )

    transformer = build_transformer(training_pipeline_params.feature_params)
    transformer.fit(train_df)

    model = train_model(
        train_df, train_marks, training_pipeline_params.train_params
    )

    inference_pipeline = create_inference_pipeline(model, transformer)

    y_pred = predict_model(
        inference_pipeline,
        test_df
    )

    metrics = evaluate_model(
        y_pred,
        test_marks
    )

    with open(training_pipeline_params.metric_path, "w") as metric_file:
        json.dump(metrics, metric_file)
    logger.info(f"Metrics :: {metrics}")

    path_to_model = serialize_model(
        inference_pipeline, training_pipeline_params.output_model_path
    )
    return path_to_model, metrics


@click.command()
@click.argument("config_path")
def main(config_path: str):
    train_pipeline(config_path)

    
if __name__ == "__main__":
    main()