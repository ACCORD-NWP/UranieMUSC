import numpy as np

from uranmusc.plotting import args_list
from uranmusc.plotting.config import Config
from uranmusc.plotting.dataset import Dataset
from uranmusc.plotting.plot import Plot
from uranmusc.plotting.util import get_uraniters


def parse_args(config_file, field):
    # get config information for field

    config_parser = Config(config_file, field)
    general_config = config_parser.get_section_config(section="general", sub_path=None)
    field_config = config_parser.get_field_config(sub_path=None)

    return general_config, field_config


def main():
    # get arguments
    args = args_list.get_args()

    # get config information
    general_config, field_config = parse_args(args.config, args.field)

    # get URANIE iterations for plotting
    iters_list = get_uraniters(
        general_config["case"]["uranTraj"], general_config["case"]["paraNum"]
    )
    field_list = []
    for uraniter in iters_list:
        # read field

        dataset = Dataset(general_config, field_config, uraniter)
        var = dataset.read_netcdf(args.field)
        field_list.append(var)

    # plotting
    if field_config["keys"]["dimensions"][0] == "time":
        # times = field_list[0].time
        times = field_list[0].coords["time"].values
        plotter = Plot(general_config, field_config, field_list, args.field)
        plotter.plot_time_series(times)
    else:
        time = field_list[0].coords["time"].values
        levels = field_list[0].coords["levels"].values
        times, _ = np.meshgrid(time, levels)
        plotter = Plot(general_config, field_config, field_list, args.field)
        plotter.plot_vertical_section(levels, times)
        plotter.plot_vertical_section(levels, times)
