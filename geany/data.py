import pandas as pd
from pathlib import Path

from hyperconf import HyperConfig
from geany.errors import GeanyError

class Dataset:
    def __init__(self, config: HyperConfig):
        if config is None:
            raise ValueError("config is None")
        self._config = config
        self._df = None

        self._outdir = Path(self._config.output_dir)
        self._outdir.mkdir(exist_ok=True, parents=True)

        
    def append(self, samples):
        if samples is None:
            raise ValueError("sample is None")
        if not isinstance(samples, dict):
            raise ValueError("sample must be a dict")

        if self._df is None:
            self._df = pd.DataFrame(samples)
        else:
            self._df = pd.concat([
                self._df,
                pd.DataFrame(samples)
            ])

    def save(self):
        df_shuffled = self._df.sample(frac=1).reset_index(drop=True)
        split_size = int(self._config.train_test_split * len(df_shuffled))
        
        train_df = df_shuffled[:split_size]
        test_df = df_shuffled[split_size:]

        if self._config.dataset_format == "csv":
            pd.to_csv(self._outdir / "train.csv")
            pd.to_csv(self._outdir / "test.csv")
        elif self._config.dataset_format == "json":
            pd.to_json(self._outdir / "train.json")
            pd.to_json(self._outdir / "test.json")
        else:
            raise GeanyError(f"the dataset format {self._config.dataset_format} is not supported")
        
