import os
import pandas as pd
import torch
from torch.utils.data import Dataset


class AnimationDataset(Dataset):
    """2D animation dataset with on-the-fly normalization."""

    def __init__(self, csv_file: str, sample_dir: str, transform=None):
        """
        Arguments:
            csv_file (string): Path to the csv file with dataset info.
            sample_dir (string): Directory with all the samples.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.sample_info = pd.read_csv(csv_file)
        self.sample_dir = sample_dir
        self.transform = transform

        # Precompute min/max for mouse and flower across the dataset
        first_sample = self._load_sample(0)
        self.mouse_min = first_sample["human_input"].min(dim=0).values
        self.mouse_max = first_sample["human_input"].max(dim=0).values
        self.flower_min = first_sample["animation"].min(dim=0).values
        self.flower_max = first_sample["animation"].max(dim=0).values

        for idx in range(1, len(self.sample_info)):
            sample = self._load_sample(idx)
            self.mouse_min = torch.min(self.mouse_min, sample["human_input"].min(dim=0).values)
            self.mouse_max = torch.max(self.mouse_max, sample["human_input"].max(dim=0).values)
            self.flower_min = torch.min(self.flower_min, sample["animation"].min(dim=0).values)
            self.flower_max = torch.max(self.flower_max, sample["animation"].max(dim=0).values)

    def _load_sample(self, idx):
        """Load a single sample without normalization."""
        sample_name = (
            self.sample_info.loc[idx, "effect_name"]
            + "_"
            + str(self.sample_info.loc[idx, "start_timestamp"])
            + "_"
            + str(self.sample_info.loc[idx, "snippet_number"])
        )
        sample_filepath = os.path.join(self.sample_dir, f"{sample_name}.csv")
        df = pd.read_csv(sample_filepath)

        mouse_cols = [col for col in df.columns if col.startswith("mouse")]
        flower_cols = [col for col in df.columns if col.startswith("flower")]

        times = torch.tensor(df[["time_s"]].values, dtype=torch.float32)
        mouse = torch.tensor(df[mouse_cols].values, dtype=torch.float32)
        flower = torch.tensor(df[flower_cols].values, dtype=torch.float32)

        return {"times": times, "human_input": mouse, "animation": flower}

    def __len__(self):
        return len(self.sample_info)

    def __getitem__(self, idx):
        sample = self._load_sample(idx)

        # Normalize mouse and animation paths to [0,1]
        mouse_norm = (sample["human_input"] - self.mouse_min) / (self.mouse_max - self.mouse_min)
        flower_norm = (sample["animation"] - self.flower_min) / (self.flower_max - self.flower_min)

        sample_norm = {
            "times": sample["times"],
            "human_input": mouse_norm,
            "animation": flower_norm,
        }

        if self.transform:
            sample_norm = self.transform(sample_norm)

        return sample_norm


if __name__ == "__main__":
    dataset = AnimationDataset(
        "animation_dataset/dataset_info.csv",
        sample_dir="animation_dataset/samples",
        transform=None,
    )

    # Check a single data point
    sample = dataset[0]
    print(sample["times"].shape, sample["human_input"].shape, sample["animation"].shape)
