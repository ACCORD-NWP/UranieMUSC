import logging
import os
import re
import shutil
import subprocess
import tempfile
import warnings
from datetime import datetime
from pathlib import Path
from typing import cast

import luigi
import yaml

from uranmusc.config_parser import Config, GitRepositoryConfig
from uranmusc.ecflow_handles import await_ecflow_node_to_complete

# Use luigi logger interface set up in uranmusc/log.py
logger = logging.getLogger("luigi-interface")

with open("config.yml", encoding="utf-8") as config_file:
    config_dict = yaml.safe_load(config_file)
    config = Config(**config_dict)


class RerunBaseTask(luigi.Task):
    """A base class for all tasks that should be rerunnable."""

    rerun = luigi.BoolParameter(default=False)
    rerun_all = luigi.BoolParameter(default=False)

    def complete(self):
        """
        If the task has any outputs, return ``True`` if all outputs exist.
        Otherwise, return ``False``. If --rerun is True, return ``False``.
        """
        if self.rerun or self.rerun_all:
            return False

        outputs = luigi.task.flatten(self.output())
        if len(outputs) == 0:
            warnings.warn(
                "Task %r without outputs has no custom complete() method" % self,
                stacklevel=2,
            )
            return False

        return all(map(lambda output: output.exists(), outputs))


class CloneRepos(RerunBaseTask):
    def output(self):
        return [luigi.LocalTarget(repo.repo / ".git") for _, repo in config.git_repos]

    def run(self):
        for repo_name, repo in config.git_repos:
            repo = cast(GitRepositoryConfig, repo)  # Make type checker happy
            logger.info(f"Removing old {repo_name} repo if it exists")
            shutil.rmtree(repo.repo, ignore_errors=True)
            logger.info(f"Cloning {repo_name} repo into '{repo.repo}'")
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--recurse-submodules",
                    "--single-branch",
                    "--branch",
                    repo.branch,
                    repo.url,
                    repo.repo,
                ],
                check=True,
            )


class SetupExperiment(RerunBaseTask):
    def requires(self):
        return CloneRepos(rerun_all=self.rerun_all)

    def output(self):
        return luigi.LocalTarget(config.home_exp_dir / "config-sh")

    def run(self):
        logger.info("Cleaning up before setting up experiment")
        for path_ in config.home_exp_dir.iterdir():

            if path_ not in [
                config.output_dir,
                config.uranie_dir,
            ]:
                logger.debug("Removing path %s", path_)
                if path_.is_dir():
                    shutil.rmtree(path_, ignore_errors=True)
                else:
                    path_.unlink(missing_ok=True)

        logger.info(f"Setting up experiment {config.experiment.name}")
        logger.info(f"Using config\n{config}")
        subprocess.run(
            [
                str(config.git_repos.harmonie.repo / "config-sh/Harmonie"),
                "setup",
                "-r",
                str(config.git_repos.harmonie.repo),
                "-h",
                "ECMWF.atos",
            ],
            cwd=config.home_exp_dir,
            check=True,
        )


class BuildExperiment(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)

    def requires(self):
        return SetupExperiment(rerun_all=self.rerun_all)

    def output(self):
        return luigi.LocalTarget(config.home_exp_dir / "experiment_is_locked")

    def run(self):
        exp_name = config.experiment.name
        bin_dir = config.general.bin_dir
        if bin_dir is not None:
            bin_dir_path = Path(bin_dir).expanduser().absolute()
            if bin_dir_path.exists():
                logger.info(
                    f"Found build dir {bin_dir_path}. Install experiment in "
                    f"{config.scratch_exp_dir} without building."
                )
                os.environ["BUILD"] = "no"
                os.environ["BINDIR"] = str(bin_dir)
            else:
                raise RuntimeError(
                    f"Could not find build dir {bin_dir_path}."
                    " Make sure to point to an existing bin dir."
                )
        else:
            logger.info(f"Building experiment {exp_name}")

        # Run the build command
        subprocess.run(
            [
                config.git_repos.harmonie.repo / "config-sh/Harmonie",
                "install",
            ],
            cwd=config.home_exp_dir,
            check=True,
            env=os.environ,
        )

        # Call your function to wait for the ecflow node to complete
        await_ecflow_node_to_complete(f"/{exp_name}")
        logger.info("Build/InitRun finished")


class SetupMusc(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)

    def requires(self):
        return [
            CloneRepos(rerun_all=self.rerun_all),
            SetupExperiment(rerun_all=self.rerun_all),
            BuildExperiment(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
        ]

    def output(self):
        output_namelist_name = f"namelist_atm_{config.experiment.musc_id}"
        return [
            luigi.LocalTarget(config.home_exp_dir / "musc_run.sh"),
            luigi.LocalTarget(config.home_exp_dir / "musc_convert_netcdf.sh"),
            luigi.LocalTarget(config.home_exp_dir / "variable_list.csv"),
            luigi.LocalTarget(config.home_exp_dir / output_namelist_name),
        ]

    def run(self):
        """Build the experiment."""
        logger.info(f"Setting up MUSC for experiment {config.experiment.name}")

        subprocess.run(
            [
                config.git_repos.harmonie.repo / "util/musc/scr/musc_setup.sh",
                "-r",
                config.git_repos.harmonie.repo,
            ],
            cwd=config.home_exp_dir,
            env={"MUSCHOME": str(config.home_exp_dir)},
            check=True,
        )

        logger.info("Generating namelist")
        subprocess.run(
            [
                config.home_exp_dir / "musc_namelist.sh",
                "-l",
                str(config.experiment.fc_length),
                "-i",
                config.experiment.musc_id,
            ],
            cwd=config.home_exp_dir,
            check=True,
        )


class RunUranie(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)

    def requires(self):
        return [
            CloneRepos(rerun_all=self.rerun_all),
            SetupExperiment(rerun_all=self.rerun_all),
            BuildExperiment(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
            SetupMusc(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
        ]

    def output(self):
        # Get settings from ura_init_nam file to determine expected output
        with open(config.experiment.ura_init_namelist, "r", encoding="utf-8") as file:
            settings = yaml.safe_load(file)
            dataserver_file_name = settings["data_files"]["dataserver"]
            namelist_template = settings["data_files"]["namelist_template"]

        return [
            luigi.LocalTarget(config.uranie_dir / dataserver_file_name),
            luigi.LocalTarget(config.scratch_exp_dir / namelist_template),
        ]

    def run(self):
        logger.info("Preparing URANIE namelist")

        with open(config.experiment.ura_init_namelist, "r", encoding="utf-8") as file_:
            uranie_init_namelist = yaml.safe_load(file_)

        # Copy over files
        shutil.copy(config.experiment.ura_init, config.scratch_exp_dir)
        shutil.copy(config.experiment.ura_init_namelist, config.scratch_exp_dir)

        # Replace variables in namelist
        namelist_template_filename = uranie_init_namelist["data_files"][
            "namelist_template"
        ]

        variables = uranie_init_namelist["variables"]["inputs"]
        with open(
            config.home_exp_dir / namelist_template_filename, "r", encoding="utf-8"
        ) as file_:
            namelist = file_.read()
            for var in variables:
                # NOTE: The space before and after @{var}@ is needed for URANIE to work
                namelist = re.sub(rf"{var}=.*", rf"{var}= @{var}@ ,", namelist, count=1)
        with open(
            config.scratch_exp_dir / namelist_template_filename, "w", encoding="utf-8"
        ) as file_:
            file_.write(namelist)

        logger.info("Running URANIE")
        subprocess.run(
            f"cd {config.scratch_exp_dir} && source {config.general.ura_env} && "
            f"python3 {config.experiment.ura_init.name} "
            f"{config.scratch_exp_dir / config.experiment.ura_init_namelist.name}",
            check=True,
            shell=True,
        )
        logger.info("URANIE finished")


class RunMusc(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)
    ntasks = luigi.IntParameter(default=1)

    def requires(self):
        return [
            CloneRepos(rerun_all=self.rerun_all),
            SetupExperiment(rerun_all=self.rerun_all),
            BuildExperiment(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
            SetupMusc(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
            RunUranie(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
        ]

    def output(self):
        # Define the expected lfa files based on the number of output dirs
        output_dirs = list(config.output_dir.glob(f"{config.experiment.musc_id}_*"))
        first_output_files = [
            output_dir / "Out.000.0000.lfa" for output_dir in output_dirs
        ]
        # Return a LocalTarget for each  file needed
        return [luigi.LocalTarget(output_file) for output_file in first_output_files]

    def complete(self):
        """
        If the task has any outputs, return ``True`` if all outputs exist.
        Otherwise, return ``False``. If --rerun is True, return ``False``.
        """
        if self.rerun_all:
            return not self.rerun_all

        uranie_output_dirs = list(config.uranie_dir.glob("UranieLauncher_*"))
        output_dirs = list(config.output_dir.glob(f"{config.experiment.musc_id}_*"))
        if len(output_dirs) != len(uranie_output_dirs):
            return False

        outputs = luigi.task.flatten(self.output())
        if len(outputs) == 0:
            warnings.warn(
                "Task %r without outputs has no custom complete() method" % self,
                stacklevel=2,
            )
            return False

        return all(map(lambda output: output.exists(), outputs))

    def run(self):
        with open(config.experiment.ura_init_namelist, "r", encoding="utf-8") as file_:
            uranie_init_namelist = yaml.safe_load(file_)

        # Replace variables in namelist
        namelist_template_filename = uranie_init_namelist["data_files"][
            "namelist_template"
        ]
        # Get missing output folders and their indices
        output_dirs = [Path(output_file.path).parent for output_file in self.output()]
        output_indices = [int(dir_.name.split("_")[2]) for dir_ in output_dirs]
        output_indices.sort()

        logger.info("Adjust URANIE namelists")
        if not output_indices:
            launcher_dirs = [
                path_ for path_ in config.uranie_dir.glob("UranieLauncher_*")
            ]
        else:
            launcher_dirs = [
                config.uranie_dir / f"UranieLauncher_{index}" for index in output_indices
            ]

        logger.info("Prepare MUSC namelists")
        commands = []
        for run_num, run_dir in enumerate(launcher_dirs, start=1):
            shutil.copy(
                run_dir / namelist_template_filename,
                config.home_exp_dir / f"{namelist_template_filename}_URA_{run_num}",
            )
            if "atm" in namelist_template_filename:
                sfx_namelist_filename = namelist_template_filename.replace("atm", "sfx")
                target_link: Path = config.home_exp_dir / (
                    sfx_namelist_filename + f"_URA_{run_num}"
                )
                target_link.unlink(missing_ok=True)
                os.symlink(config.home_exp_dir / sfx_namelist_filename, target_link)
            elif "sfx" in namelist_template_filename:
                atm_namelist_filename = namelist_template_filename.replace("sfx", "atm")
                target_link = (
                    config.home_exp_dir / f"{atm_namelist_filename}_URA_{run_num}"
                )
                target_link.unlink(missing_ok=True)
                os.symlink(config.home_exp_dir / atm_namelist_filename, target_link)
            else:
                raise ValueError("Unknown namelist type")
            commands.append(
                f"{config.home_exp_dir / 'musc_run.sh'} "
                f"-d {config.general.musc_data_dir} "
                f"-n {config.experiment.musc_case} "
                f"-i {config.experiment.musc_id}_URA_{run_num}"
            )

        with tempfile.NamedTemporaryFile(
            "w", dir=config.home_exp_dir, delete=False
        ) as tmp:
            tmp.write("#!/bin/bash\n")
            tmp.write("#SBATCH --job-name=RUN_MUSC\n")
            tmp.write("#SBATCH --qos=nf\n")
            tmp.write(f"#SBATCH --ntasks={min(len(commands), self.ntasks)}\n")
            tmp.write("#SBATCH --mem-per-cpu=10GB\n")
            tmp.write("#SBATCH --time=00:15:00\n")
            tmp.write("#SBATCH --threads-per-core=1\n")
            tmp.write(f"#SBATCH -o {config.home_exp_dir / 'RUN_MUSC-slurm-%j.out'}\n")
            tmp.write(f"#SBATCH -e {config.home_exp_dir / 'RUN_MUSC-slurm-%j.out'}\n")
            tmp.write(f"cd {config.home_exp_dir}\n")
            tmp.write(" &\n".join(commands))
            tmp.write("\nwait\n")
            os.chmod(tmp.name, 0o755)

        logger.info(
            "Running MUSC from launcher dirs {}".format(
                [dir_.name for dir_ in launcher_dirs]
            )
        )
        subprocess.run(
            ["sbatch", "--wait", tmp.name], check=True, cwd=config.home_exp_dir
        )
        logger.info("MUSC finished")
        os.unlink(tmp.name)


class BuildDDH(RerunBaseTask):
    def output(self):
        lfac_path = config.git_repos.ddhtoolbox.repo / "tools/lfa/lfac"
        return luigi.LocalTarget(lfac_path)

    def requires(self):
        return CloneRepos(rerun_all=self.rerun_all)

    def run(self):
        logger.info("Installing DDH library")
        subprocess.run(
            "export PATH=.:$PATH; install clean; install;",
            cwd=config.git_repos.ddhtoolbox.repo / "tools",
            check=True,
            shell=True,
        )
        logger.info("Done installing DDH library")


class ConvertLFAToNetCDF(RerunBaseTask):
    bin_dir = luigi.Parameter(default=None)
    ntasks = luigi.IntParameter(default=1)

    def requires(self):
        return [
            BuildDDH(rerun_all=self.rerun_all),
            CloneRepos(rerun_all=self.rerun_all),
            SetupExperiment(rerun_all=self.rerun_all),
            BuildExperiment(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
            SetupMusc(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
            RunUranie(bin_dir=self.bin_dir, rerun_all=self.rerun_all),
            RunMusc(
                bin_dir=self.bin_dir,
                ntasks=self.ntasks,
                rerun_all=self.rerun_all,
            ),
        ]

    def output(self):
        # Define the expected nc files based on the number of output dirs
        output_dirs = list(config.output_dir.glob(f"{config.experiment.musc_id}_*"))
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
        output_dirs = list(config.output_dir.glob(f"{config.experiment.musc_id}_*"))
        for dir_ in output_dirs:
            shutil.copytree(
                config.home_exp_dir / "config-sh",
                dir_ / "config-sh",
                dirs_exist_ok=True,
            )

        commands = [
            f"{config.home_exp_dir / 'musc_convert_netcdf.sh'}"
            + f" -e {dir_} -v {config.home_exp_dir / 'variable_list.csv'} &"
            for dir_ in output_dirs
        ]
        ddhtoolbox_repo = config.git_repos.ddhtoolbox.repo
        with tempfile.NamedTemporaryFile(
            "w", dir=config.home_exp_dir, delete=False
        ) as tmp:
            tmp.write("#!/bin/bash\n")
            tmp.write("#SBATCH --job-name=MUSC_CV_NC\n")
            tmp.write("#SBATCH --qos=nf\n")
            tmp.write(f"#SBATCH --ntasks={min(len(commands), self.ntasks)}\n")
            tmp.write("#SBATCH --mem-per-cpu=8GB\n")
            tmp.write("#SBATCH --time=00:15:00\n")
            tmp.write("#SBATCH --threads-per-core=1\n")
            tmp.write(f"#SBATCH -o {config.home_exp_dir / 'MUSC_CV_NC-slurm-%j.out'}\n")
            tmp.write(f"#SBATCH -e {config.home_exp_dir / 'MUSC_CV_NC-slurm-%j.out'}\n")
            tmp.write(f"export PATH={ddhtoolbox_repo}/tools/lfa:$PATH\n")
            tmp.write(f"export PATH={ddhtoolbox_repo}/tools:$PATH\n")
            tmp.write(f"cd {config.home_exp_dir}\n")
            tmp.write(" \n".join(commands))
            tmp.write("\nwait")
            os.chmod(tmp.name, 0o755)

        logger.info("Converting LFA files to NetCDF")
        subprocess.run(
            ["sbatch", "--wait", tmp.name], check=True, cwd=config.home_exp_dir
        )
        logger.info("Done converting LFA files to NetCDF")
        os.unlink(tmp.name)


class Run(luigi.WrapperTask):
    bin_dir = luigi.Parameter(default=None)
    ntasks = luigi.IntParameter(default=1)
    rerun_all = luigi.BoolParameter(default=False)

    def requires(self):
        yield ConvertLFAToNetCDF(
            bin_dir=self.bin_dir, ntasks=self.ntasks, rerun_all=self.rerun_all
        )
