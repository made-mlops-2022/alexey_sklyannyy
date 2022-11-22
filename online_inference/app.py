import logging
import os
import pickle

import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI
from typing import (
    List,
    Union
)

from pydantic import (
    BaseModel,
    conlist
)

from sklearn.ensemble import (
    RandomForestClassifier,
)
from sklearn.pipeline import Pipeline

from utils import on_inf_logger


class ConditionResponse(BaseModel):
    id: int
    condition: int

class Request(BaseModel):
    data: List[conlist(Union[float, str, None], min_items=80, max_items=80)]
    features: List[str]

def load_object(path: str) -> Pipeline:
    with open(path, "rb") as load:
        return pickle.load(load)


def make_predict(
    data: List, features: List[str], model: Pipeline
) -> List[ConditionResponse]:
    data = pd.DataFrame(data, columns=features)
    ids = [int(x) for x in data["Id"]]
    predicts = model.predict(data)

    on_inf_logger.info(f"make_predict :: predicts( {predicts} ) ")

    return [ConditionResponse(id=id_, condition=cond_)
        for id_, cond_ in zip(ids, predicts)
    ]

app = FastAPI()

@app.get("/")
def main():
    return "Main Directory"

@app.on_event("startup")
def load_model():
    global model
    model_path = os.getenv("PATH_TO_MODEL")
    if model_path is None:
        err = f"PATH_TO_MODEL {model_path} is None"
        on_inf_logger.error(err)
        raise RuntimeError(err)

    model = load_object(model_path)

@app.get("/status")
def status():
    return f"Model ready status :: ( {model is not None} )"

@app.get("/predict", response_model=List[ConditionResponse])
def predict(request: Request):
    print("debug")
    on_inf_logger.debug("debug")
    return make_predict(
        request.data,
        request.features,
        model
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=os.getenv("PORT", 8000))