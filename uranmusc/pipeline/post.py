import logging
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import luigi

from uranmusc.pipeline.build import BuildDDH, BuildExperiment
from uranmusc.pipeline.pre import CloneRepos
from uranmusc.pipeline.run import RerunBaseTask, RunMusc, RunUranie
from uranmusc.pipeline.setup_experiment import SetupExperiment
from uranmusc.pipeline.setup_musc import SetupMusc

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class ConvertLFAToNetCDF(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)
    ntasks = luigi.IntParameter(default=1)

    def requires(self):
        return [
            BuildDDH(rerun_all=self.rerun_all, config=self.config),
            CloneRepos(rerun_all=self.rerun_all, config=self.config),
            SetupExperiment(rerun_all=self.rerun_all, config=self.config),
            BuildExperiment(
                bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config
            ),
            SetupMusc(bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config),
            RunUranie(bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config),
            RunMusc(
                bin_dir=self.bin_dir,
                ntasks=self.ntasks,
                rerun_all=self.rerun_all,
                config=self.config,
            ),
        ]

    def output(self):
        # Define the expected nc files based on the number of output dirs
        uranie_output_dirs = list(self.config.uranie_dir.glob("UranieLauncher_*"))
        run_numbers = [int(dir_.name.split("_")[1]) for dir_ in uranie_output_dirs]
        output_dirs = sorted(
            dir_
            for run_number in run_numbers
            for dir_ in self.config.output_dir.glob(
                f"{self.config.experiment.musc_id}_*_{run_number}_*"
            )
        )
        example_files = [next(output_dir.glob("*")) for output_dir in output_dirs]
        date_strings = list(
            datetime.fromtimestamp(os.path.getctime(file_)).strftime("%y%m%d")
            for file_ in example_files
        )
        nc_files = list(
            Path(output_dir) / f"musc_output_{date_str}.nc"
            for output_dir, date_str in zip(output_dirs, date_strings)
        )
        # Return a LocalTarget for each .nc file needed
        return [luigi.LocalTarget(nc_file) for nc_file in nc_files]

    def run(self):
        # Copy over specific files to prepare for running conversion from output dirs
        output_dirs = [Path(output_file.path).parent for output_file in self.output()]
        for dir_ in output_dirs:
            shutil.copytree(
                self.config.home_exp_dir / "config-sh",
                dir_ / "config-sh",
                dirs_exist_ok=True,
            )

        commands = [
            f"{self.config.home_exp_dir / 'musc_convert_netcdf.sh'}"
            + f" -e {dir_} -v {self.config.home_exp_dir / 'variable_list.csv'} &"
            for dir_ in output_dirs
        ]
        ddhtoolbox_repo = self.config.git_repos.ddhtoolbox.repo
        with tempfile.NamedTemporaryFile(
            "w", dir=self.config.home_exp_dir, delete=False
        ) as tmp:
            tmp.write("#!/bin/bash\n")
            tmp.write("#SBATCH --job-name=MUSC_CV_NC\n")
            tmp.write("#SBATCH --qos=nf\n")
            tmp.write(f"#SBATCH --ntasks={min(len(commands), self.ntasks)}\n")
            tmp.write("#SBATCH --mem-per-cpu=8GB\n")
            tmp.write("#SBATCH --time=00:15:00\n")
            tmp.write("#SBATCH --threads-per-core=1\n")
            tmp.write(
                f"#SBATCH -o {self.config.home_exp_dir / 'MUSC_CV_NC-slurm-%j.out'}\n"
            )
            tmp.write(
                f"#SBATCH -e {self.config.home_exp_dir / 'MUSC_CV_NC-slurm-%j.out'}\n"
            )
            tmp.write(f"export PATH={ddhtoolbox_repo}/tools/lfa:$PATH\n")
            tmp.write(f"export PATH={ddhtoolbox_repo}/tools:$PATH\n")
            tmp.write(f"cd {self.config.home_exp_dir}\n")
            tmp.write(" \n".join(commands))
            tmp.write("\nwait")
            os.chmod(tmp.name, 0o755)

        logger.info("Converting LFA files to NetCDF")
        subprocess.run(
            ["sbatch", "--wait", tmp.name], check=True, cwd=self.config.home_exp_dir
        )
        logger.info("Done converting LFA files to NetCDF")
        os.unlink(tmp.name)
