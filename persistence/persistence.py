import numpy as np
import os
import tqdm
import gudhi as gd

class CubicalCPH:
    def __init__(self, **kwargs):
        """
        Initialize CubicalCPH with specified parameters.

        Parameters:
        - dataset (str): Name of the dataset. Default: "TNG50-1-Dark".
        - snapshot (int): Snapshot number. Default: 99.
        - crop (int): Percentage of data to keep after cropping. Default: 12.
        """
        self.dataset = kwargs.get("dataset", "TNG50-1-Dark")
        self.snapshot = kwargs.get("snapshot", 99)
        self.crop = kwargs.get("crop", 12)

    def compute_persistence_homology(self, points):
        """
        Compute persistence diagrams for a given set of points using Cubical Complex.

        Parameters:
        - points (np.array): Input point cloud.

        Returns:
        Tuple: Persistence diagrams in dimensions 0, 1, and 2.
        """
        cubical_complex = gd.CubicalComplex(vertices=points)
        cubical_complex.compute_persistence()
        return (
            cubical_complex.persistence_intervals_in_dimension(0),
            cubical_complex.persistence_intervals_in_dimension(1),
            cubical_complex.persistence_intervals_in_dimension(2)
        )

    def run(self):
        """
        Execute the main workflow of CubicalCPH.

        This includes reading data, computing persistence diagrams,
        and saving the output.
        """
        with tqdm.tqdm(total=100, desc="Approximating PH", colour="red") as pbar:
            data_path = os.path.join(os.getcwd(), "data", self.dataset, f"snap_0{self.snapshot}")
            densities_file = os.path.join(data_path, "preprocessed", f"densities_C{self.crop}.txt")

            pbar.set_description("Loading DTFE Object")
            dtfe = np.loadtxt(densities_file)
            grid_size = int(dtfe[:, 0].max()) + 1
            reshaped_dtfe = dtfe[:, -1].reshape((grid_size, grid_size, grid_size))
            log_dtfe = np.log(reshaped_dtfe + np.ones_like(reshaped_dtfe))
            pbar.update(50)

            print(log_dtfe.shape)
            pbar.colour = "yellow"
            pbar.set_description("Computing Cubical Complex Persistence")
            ph_dim0, ph_dim1, ph_dim2 = self.compute_persistence_homology(log_dtfe)

            pbar.update(50)
            pbar.colour = "green"
            pbar.set_description("Done Approx PH")

            output_path = os.path.join(data_path, "cubical")
            os.makedirs(output_path, exist_ok=True)
            
            np.savetxt(os.path.join(output_path, f"DTFE_dim0_C{self.crop}.txt"), ph_dim0)
            np.savetxt(os.path.join(output_path, f"DTFE_dim1_C{self.crop}.txt"), ph_dim1)
            np.savetxt(os.path.join(output_path, f"DTFE_dim2_C{self.crop}.txt"), ph_dim2)

