import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import luigi

from uranmusc.pipeline.base import RerunBaseTask
from uranmusc.pipeline.build import BuildExperiment
from uranmusc.pipeline.pre import CloneRepos
from uranmusc.pipeline.setup_experiment import SetupExperiment
from uranmusc.pipeline.setup_musc import SetupMusc, SetupMuscNamelists

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")


class RunUranie(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)

    def requires(self):
        return [
            CloneRepos(rerun_all=self.rerun_all, config=self.config),
            SetupExperiment(rerun_all=self.rerun_all, config=self.config),
            BuildExperiment(
                bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config
            ),
            SetupMusc(bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config),
            SetupMuscNamelists(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
        ]

    def output(self):
        doe = self.config.experiment.design_of_experiment
        return [
            luigi.LocalTarget(self.config.uranie_dir / doe.data_files.dataserver),
            luigi.LocalTarget(
                self.config.scratch_exp_dir / self.config.namelist_atm.name
            ),
        ]

    def run(self):
        logger.info("Preparing URANIE namelist")
        doe = self.config.experiment.design_of_experiment
        # Dump DOE config to temporary file
        tmp_doe_file = tempfile.NamedTemporaryFile("w", delete=False, suffix=".yml")
        doe.to_yaml(tmp_doe_file.name, musc_id=self.config.experiment.musc_id)

        # Update and write namelist file to experiment dir
        with open(self.config.namelist_atm, "r", encoding="utf-8") as file_:
            namelist = file_.read()
            for var in doe.variables.inputs:
                # NOTE: The space before and after @{var}@ is needed for URANIE to work
                namelist = re.sub(rf"{var}=.*", rf"{var}= @{var}@ ,", namelist, count=1)
        with open(
            self.config.scratch_exp_dir / self.config.namelist_atm.name,
            "w",
            encoding="utf-8",
        ) as file_:
            file_.write(namelist)

        logger.info("Running URANIE")
        subprocess.run(
            f"cd {self.config.scratch_exp_dir} && "
            f"source {self.config.general.ura_env} && uv run python "
            f"{self.config.project_dir / 'uranmusc/design_of_experiment.py'} "
            f"{tmp_doe_file.name}"
            f" --output-dir {self.config.uranie_dir} "
            f" --namelist-dir {self.config.scratch_exp_dir}",
            check=True,
            shell=True,
        )
        logger.info("URANIE finished")
        # Clean up
        os.unlink(tmp_doe_file.name)


class RunMusc(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)
    ntasks = luigi.IntParameter(default=1)

    def requires(self):
        return [
            CloneRepos(rerun_all=self.rerun_all, config=self.config),
            SetupExperiment(rerun_all=self.rerun_all, config=self.config),
            BuildExperiment(
                bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config
            ),
            SetupMusc(bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config),
            RunUranie(bin_dir=self.bin_dir, rerun_all=self.rerun_all, config=self.config),
        ]

    def output(self):
        # Define the expected lfa files based on the number of output dirs
        uranie_output_dirs = list(self.config.uranie_dir.glob("UranieLauncher_*"))
        run_numbers = [int(dir_.name.split("_")[1]) for dir_ in uranie_output_dirs]
        output_dirs = sorted(
            dir_
            for run_number in run_numbers
            for dir_ in self.config.output_dir.glob(
                f"{self.config.experiment.musc_id}_*_{run_number}_*"
            )
        )
        first_output_files = [
            output_dir / "Out.000.0000.lfa" for output_dir in output_dirs
        ]
        # Return a LocalTarget for each  file needed
        return [luigi.LocalTarget(output_file) for output_file in first_output_files]

    def run(self):
        # Get missing output folders and their indices
        output_dirs = [Path(output_file.path).parent for output_file in self.output()]
        output_indices = [int(dir_.name.split("_")[2]) for dir_ in output_dirs]
        output_indices.sort()

        uranie_launcher_dirs = list(self.config.uranie_dir.glob("UranieLauncher_*"))

        logger.info("Adjust URANIE namelists")
        if not output_indices or len(uranie_launcher_dirs) != len(output_indices):
            launcher_dirs = [
                path_ for path_ in self.config.uranie_dir.glob("UranieLauncher_*")
            ]
        else:
            launcher_dirs = [
                self.config.uranie_dir / f"UranieLauncher_{index}"
                for index in output_indices
            ]

        logger.info("Prepare MUSC namelists")
        commands = []
        for run_num, run_dir in enumerate(launcher_dirs, start=1):
            shutil.copy(
                run_dir / self.config.namelist_atm.name,
                self.config.home_exp_dir
                / f"{self.config.namelist_atm.name}_URA_{run_num}",
            )
            target_link: Path = self.config.home_exp_dir / (
                self.config.namelist_sfx.name + f"_URA_{run_num}"
            )
            target_link.unlink(missing_ok=True)
            os.symlink(
                self.config.home_exp_dir / self.config.namelist_sfx.name, target_link
            )
            target_link = (
                self.config.home_exp_dir
                / f"{self.config.namelist_atm.name}_URA_{run_num}"
            )
            target_link.unlink(missing_ok=True)
            os.symlink(
                self.config.home_exp_dir / self.config.namelist_atm.name, target_link
            )

            commands.append(
                f"{self.config.home_exp_dir / 'musc_run.sh'} "
                f"-d {self.config.general.musc_data_dir} "
                f"-n {self.config.experiment.musc_case} "
                f"-i {self.config.experiment.musc_id}_URA_{run_num}"
            )

        with tempfile.NamedTemporaryFile(
            "w", dir=self.config.home_exp_dir, delete=False
        ) as tmp:
            tmp.write("#!/bin/bash\n")
            tmp.write("#SBATCH --job-name=RUN_MUSC\n")
            tmp.write("#SBATCH --qos=nf\n")
            tmp.write(f"#SBATCH --ntasks={min(len(commands), self.ntasks)}\n")
            tmp.write("#SBATCH --mem-per-cpu=10GB\n")
            tmp.write("#SBATCH --time=00:15:00\n")
            tmp.write("#SBATCH --threads-per-core=1\n")
            tmp.write(
                f"#SBATCH -o {self.config.home_exp_dir / 'RUN_MUSC-slurm-%j.out'}\n"
            )
            tmp.write(
                f"#SBATCH -e {self.config.home_exp_dir / 'RUN_MUSC-slurm-%j.out'}\n"
            )
            tmp.write(f"cd {self.config.home_exp_dir}\n")
            tmp.write(" &\n".join(commands))
            tmp.write("\nwait\n")
            os.chmod(tmp.name, 0o755)

        logger.info(
            "Running MUSC from launcher dirs {}".format(
                [dir_.name for dir_ in launcher_dirs]
            )
        )
        subprocess.run(
            ["sbatch", "--wait", tmp.name], check=True, cwd=self.config.home_exp_dir
        )
        logger.info("MUSC finished")
        os.unlink(tmp.name)
