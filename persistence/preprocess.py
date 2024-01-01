import os
import h5py
import requests
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tqdm
import time

class Preprocess:
    def __init__(self, **kwargs):
        """
        Initialize Preprocess with specified parameters.
        Parameters:
        - tune: if True enables grid search for HDBSCAN parameters.
        - dataset: Name of the dataset.
        - snapshot: Snapshot number.
        - headers: HTTP headers for API requests.
        - crop: Percentage of data to keep after cropping.
        - minmass: Minimum mass threshold for filtering data.
        """
        self.dataset = kwargs.get("dataset", "TNG50-1-Dark")
        self.snapshot = kwargs.get("snapshot", 99)
        self.headers = kwargs.get("headers", {"api-key": "ADD-API-KEY"})
        self.crop = kwargs.get("crop", 40)
        self.minmass = kwargs.get("minmass", 0)

    @staticmethod
    def crop_dataset(dataset, crop_percent):
        """
        Crop the dataset to a specified percentage around the center.
        Parameters:
        - dataset: Input dataset.
        - crop_percent: Percentage of data to keep after cropping.
        Returns:
        Cropped dataset.
        """
        center = np.median(dataset, axis=0)
        size = np.ptp(dataset, axis=0)
        crop_size = crop_percent / 100.0 * np.max(size)
        mask = np.all(
            np.logical_and(
                dataset >= center - crop_size / 2,
                dataset <= center + crop_size / 2
            ),
            axis=1
        )
        return dataset[mask]

    def get(self, path, params):
        """
        Download data from a specified URL.
        Parameters:
        - path: URL for the GET request.
        - params: Parameters for the GET request.
        """
        response = requests.get(path, params=params, headers=self.headers)
        response.raise_for_status()
        filename = response.headers["content-disposition"].split("filename=")[1]
        output_path = os.path.join(os.getcwd(), "data", self.dataset, f"snap_0{self.snapshot}")
        os.makedirs(output_path, exist_ok=True)
        with open(os.path.join(output_path, filename), "wb") as file:
            file.write(response.content)

    def filters(self, dataset, masses, normalize=True):
        """
        Apply mass filtering and normalization to the dataset.
        Parameters:
        - dataset: Input dataset.
        - masses: Mass values associated with each data point.
        - normalize: Whether to normalize the data.
        Returns:
        Filtered and optionally normalized dataset.
        """
        filtered_data = dataset[masses >= self.minmass]
        cropped_data = self.crop_dataset(filtered_data, self.crop)
        return MinMaxScaler(feature_range=(-1, 1)).fit_transform(cropped_data) if normalize else cropped_data

    def run(self):
        """
        Main workflow for preprocessing data.
        """
        with tqdm.tqdm(total=100, desc="Preprocessing Data", colour="red") as pbar:
            data_dir = os.path.join(os.getcwd(), "data", self.dataset, f"snap_0{self.snapshot}")
            preprocessed_dir = os.path.join(data_dir, "preprocessed")
            os.makedirs(preprocessed_dir, exist_ok=True)

            pbar.set_description("Checking data availability")
            time.sleep(1)  # Simulate delay for checking
            file_suffix = f"fof_subhalo_tab_0{self.snapshot}.Subhalo"
            if not os.path.exists(os.path.join(data_dir, f"{file_suffix}.SubhaloPos.hdf5")) or \
               not os.path.exists(os.path.join(data_dir, f"{file_suffix}.SubhaloMass.hdf5")):
                pbar.set_description("Downloading data")
                base_url = f"http://www.tng-project.org/api/{self.dataset}/files/groupcat-{self.snapshot}/"
                self.get(base_url, {"Subhalo": "SubhaloMass"})
                self.get(base_url, {"Subhalo": "SubhaloPos"})
            else:
                pbar.set_description("Data already present")
            pbar.update(33)

            with h5py.File(os.path.join(data_dir, f"{file_suffix}.SubhaloPos.hdf5"), "r") as file:
                subhalos = file["Subhalo"]["SubhaloPos"][:, :]
            with h5py.File(os.path.join(data_dir, f"{file_suffix}.SubhaloMass.hdf5"), "r") as file:
                masses = file["Subhalo"]["SubhaloMass"][:]

            pbar.set_description("Filtering data")
            data = self.filters(subhalos, masses)
            data_unnormalized = self.filters(subhalos, masses, normalize=False)
            np.savetxt(os.path.join(preprocessed_dir, f"raw_C{self.crop}.txt"), data, delimiter=" ", header="\n".join([f"{data.shape[0]}", "-1 1 -1 1 -1 1"]), comments="")
            np.savetxt(os.path.join(preprocessed_dir, f"raw_unnormalized_C{self.crop}.txt"), data_unnormalized, delimiter=" ", header="\n".join([f"{data.shape[0]}", "-1 1 -1 1 -1 1"]), comments="")
            pbar.update(66)
            pbar.set_description("Done preprocessing")
            time.sleep(1)  # Simulate final processing delay
