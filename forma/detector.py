# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/detector.ipynb (unless otherwise specified).

__all__ = ['FormatDetector']

# Cell
import numpy as np
import pandas as pd

from typing import Any, Dict, Callable
from tqdm import tqdm

from .judge import FormatJudge
from .utils import PatternGenerator

# Cell
class FormatDetector:
    def __init__(self, skip: list = None):
        self.skip = skip

    def fit(self, df: pd.DataFrame, generator: PatternGenerator or List['str': PatternGenerator],
            n: int = 3, dim: int = 1):
        self.judges = {}

        self.df = df
        with tqdm(total=len(self.df.columns)) as pbar:
            if isinstance(generator, PatternGenerator):
                for col in self.df.columns:
                    if col in self.skip:
                        continue
                    col_values = self.df[col].tolist()
                    format_judge = FormatJudge(generator, n, dim)
                    format_judge.fit(col_values)
                    self.judges[col] = format_judge
                    pbar.update(1)
            else:
                for col in self.df.columns:
                    if col in self.skip:
                        continue
                    col_values = self.df[col].tolist()
                    gen = generator.get(col, PatternGenerator())
                    format_judge = FormatJudge(gen, n, dim)
                    format_judge.fit(col_values)
                    self.judges[col] = format_judge
                    pbar.update(1)

    def detect(self, reduction: Callable = np.min, softmax: bool = True) -> dict:
        scores = []

        with tqdm(total=len(self.df)) as pbar:
            for index, row in self.df.iterrows():
                tuple_score = []
                for col in self.df.columns:
                    if col in self.skip:
                        continue
                    judge = self.judges[col]
                    score = np.mean(judge(row[col]))
                    tuple_score.append(score)
                if softmax:
                    tuple_score = np.exp(tuple_score)
                    softmax_tuple_score = [score / sum(tuple_score) for score in tuple_score]
                    if reduction == np.ptp:
                        scores.append(reduction(softmax_tuple_score))
                    else:
                        scores.append(1 - reduction(softmax_tuple_score))
                else:
                    if reduction == np.ptp:
                        scores.append(reduction(tuple_score))
                    else:
                        scores.append(1 - reduction(tuple_score))
                pbar.update(1)
        assessed_df = self.df.copy()
        assessed_df['p'] = scores
        return assessed_df