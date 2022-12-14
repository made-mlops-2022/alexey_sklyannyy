from dataclasses import dataclass
import pandas as pd


@dataclass
class SplitParams:
    test_size: float = 0.2
    random_state: int = 0

@dataclass
class SplitData:
    X: pd.DataFrame
    y: pd.DataFrame
