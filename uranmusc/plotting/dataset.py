#!/usr/bin/env python3

import glob

import numpy as np
import xarray as xr


# ============================================================================#
class Dataset:
    def __init__(self, general_config, field_config, uraniter):
        self.general_config = general_config
        self.general_case_config = self.general_config.get("case")
        self.field_keys_config = field_config["keys"]
        self.field_preprocess_config = field_config["preprocess"]
        self.uraniter = uraniter
        self.field = None
        # initialize empty dict
        # self.data = {} #

    # filedir needs to be updated dynamically
    @property
    def filedir(self):

        data_path = (
            f'{self.general_config["basedir"]}'
            f"/OUTPUT"
            f'/{self.general_case_config["muscID"]}_'
            f"URA_{self.uraniter}_"
            f'{self.general_case_config["outputInfo"]}'
        )

        return f'{data_path}/musc_output_{self.general_case_config["outputDate"]}.nc'

    def lfafiles(self):
        """get Out*lfa files"""

        output_dir = (
            f'{self.general_case_config["caseName"]}_URA_'
            f'{self.uraniter}_{self.general_case_config["outputInfo"]}'
        )
        files = glob.glob(f"{output_dir}/" + "Out*.lfa")
        files = np.sort(files)

        return files

    # def read_lfa(self, fid):

    #     ds = epygram.formats.resource(self.filedir, "r")

    #     self.field = self.preprocess(ds.readfield(fid))

    #     return self.field

    def read_netcdf(self, varname):

        ds = xr.open_dataset(self.filedir)

        self.field = self._preprocess(ds[varname])

        return self.field

    def _preprocess(self, field):
        """
        preprocess variable if needed
        """
        operation = self.field_preprocess_config["operator"]
        offset = self.field_preprocess_config["offset"]

        if operation == "add":

            return field + offset

        elif operation == "multiply":

            return field * offset

        elif operation == "":

            return field

    def sum_over_dim(self, field, dim):
        """
        sum field over dimension dim
        """
        field_sum = field.sum(dim=dim, keep_attrs=True)

        return field_sum


class Uranie:
    def __init__(self, general_config):
        self.general_config = general_config

    def read_init_doe(self):

        doe_fil = f'{self.general_config["basedir"]}' f"/URANIE" f"/init_doe.dat"

        init_doe = np.loadtxt(doe_fil, comments="#")
        para_value = []

        for i in range(len(init_doe)):
            para_value.append(init_doe[i][0])

        with open(doe_fil, "r") as f:
            for line in f:
                if line.startswith("#COLUMN_NAMES:"):
                    parts = line.strip().split(":")[1].split("|")
                    para_name = parts[0].strip()

        if para_name == "RFRMIN(9)":
            para_name = "ICENU"
        elif para_name == "RFRMIN(10)":
            para_name = "KGN_ACON"
        elif para_name == "RFRMIN(11)":
            para_name = "KGN_SBGR"

        return para_name, para_value
