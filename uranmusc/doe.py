from rootlogon import *
import yaml
import sys
import os


def usage():
    print("Usage: python3 doe.py <yaml-file>")
    print("Example: python URA_EGO.py doe.yml")


FILES = ["dataserver", "namelist_template"]
VARIABLES = ["inputs", "minima", "maxima", "namelist_flags"]
DOE = ["sample_size", "distribution"]


def parse_yaml(yaml_file):
    with open(yaml_file, "r") as file:
        settings = yaml.safe_load(file)
    missing_keys = []
    for key in FILES:
        if key not in settings["data_files"].keys():
            missing_keys.append(key)
        else:
            if not settings["data_files"][key]:
                missing_keys.append(key)
    for key in VARIABLES:
        if key not in settings["variables"].keys():
            missing_keys.append(key)
        else:
            if not settings["variables"][key]:
                missing_keys.append(key)
    for key in DOE:
        if key not in settings["doe"].keys():
            missing_keys.append(key)
        else:
            if not settings["doe"][key]:
                missing_keys.append(key)

    if missing_keys:
        raise KeyError(f"Following keys are missing in the YAML-file: {missing_keys}")

    inputs = dict()
    for i, var in enumerate(settings["variables"]["inputs"]):
        inputs[var] = {
            "min": settings["variables"]["minima"][i],
            "max": settings["variables"]["maxima"][i],
            "flag": settings["variables"]["namelist_flags"][i],
        }
    return (settings, inputs)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
        sys.exit(1)
    else:
        yaml_file = sys.argv[1]

    # 0. Parse the namelist file
    settings, inputs = parse_yaml(yaml_file)
    namdir = os.path.dirname(yaml_file)
    # 1. Create the URANIE dataserver
    ds = DataServer.TDataServer("tds", "Design of Experiment")
    for var in inputs:
        ds.addAttribute(
            DataServer.TUniformDistribution(var, inputs[var]["min"], inputs[var]["max"])
        )
        ds.getAttribute(var).setFileFlag(
            os.path.join(namdir, settings["data_files"]["namelist_template"]),
            inputs[var]["flag"],
        )

    # 2. Create the Dummy model
    dummy_model = Launcher.TCode(ds, "echo Running dummy model; echo OK | cat > out.dat")
    output_file = Launcher.TOutputFileKey("out.dat")
    dummy_model.addOutputFile(output_file)

    # 3. Create samples
    sampler = Sampler.TSampling(
        ds, settings["doe"]["distribution"], settings["doe"]["sample_size"]
    )
    sampler.generateSample()

    # 3. Create Launcher and run the model
    launcher = Launcher.TLauncher(ds, dummy_model)
    launcher.setSave()
    launcher.setClean()
    launcher.run()

    # 4. Export the dataserver
    ds.exportData(os.path.join("./URANIE", settings["data_files"]["dataserver"]))
