#!/usr/bin/env python3

import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from mpl_toolkits.axes_grid1 import make_axes_locatable

from uranmusc.plotting.dataset import Uranie

# ============================================================================#
font_dirs = "/perm/iczx/EPyGrAM/mscorefonts-0.0.1-3"
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
for font_file in font_files:
    font_manager.fontManager.addfont(font_file)


class Plot:
    def __init__(self, general_config, field_config, field, shortname):

        self.general_config = general_config
        self.plot_config = field_config["plot"]
        self.preprocess_config = field_config["preprocess"]
        self.field = field
        self.shortname = shortname

        # get the parameter and parameter values are tested
        uranInfo = Uranie(general_config)
        self.para_name, self.para_val = uranInfo.read_init_doe()

    def create_panel_fig_init(self, fig_num):

        ncols = math.ceil(math.sqrt(fig_num)) + 1
        nrows = math.ceil(fig_num / ncols)

        figsize = (ncols * 12, nrows * 12)

        fig, axs = plt.subplots(
            nrows=nrows,
            ncols=ncols,
            figsize=figsize,
            layout="constrained",
            gridspec_kw={"wspace": 0.1, "hspace": 0.05},
        )
        # constrained_layout=True)

        # keep axs for the first num
        axlist = axs.flatten()[:fig_num]
        for i, ax in enumerate(axs.flatten()):
            if i > fig_num - 1:
                fig.delaxes(ax)

        # fig.subplots_adjust(bottom=0.13,top=0.9,left=0.1,right=0.9,wspace=0.18,hspace=0.06)
        # fig.tight_layout()

        return fig, axlist

    def add_title(self, ax, left_label, center_label):
        """add title"""
        # left title
        ax.set_title(f"Uran: {left_label}", loc="left", fontsize=20, fontweight="bold")

        ax.set_title(
            f"{self.para_name}: {center_label}",
            loc="center",
            fontsize=20,
            fontweight="bold",
        )

        ax.set_title(f"{self.shortname}", loc="right", fontsize=20, fontweight="bold")

    def add_colorbar(self, plot, fig, ax, ticks):
        """add colorbar"""

        labelCB = f"{self.plot_config['cbar_name']} ({self.preprocess_config['units']})"
        cax = make_axes_locatable(ax).append_axes(
            "right", size="2.5%", pad=0.1, axes_class=plt.Axes
        )
        cbar = fig.colorbar(plot, cax=cax, ticks=ticks[:], orientation="vertical")
        cbar.ax.tick_params(labelsize=16)
        cbar.set_label(label=labelCB, labelpad=-1.1, y=0.5, rotation=90, size=16)
        ax.tick_params(axis="both", labelsize=6, direction="out")

    def save_fig(self, fig):
        """save figure"""
        # figure name
        iters = str(len(self.para_val))
        figname = (
            f"{self.shortname}_"
            f"{self.para_name}_"
            f"{self.general_config['case']['caseName']}_"
            f"Uran{iters}.png"
        )

        save_kwargs = dict(bbox_inches="tight", dpi=self.plot_config["figure_dpi"])
        # create a new directory for saving figures if it does not exist
        casedir = (
            f"musc_uranie_{self.general_config['case']['muscCycle']}_"
            f"{self.general_config['case']['caseName']}_"
            f"{self.para_name}"
        )
        savedir = Path(self.general_config["savedir"] + "/" + casedir)
        print(savedir)
        if not savedir.exists():
            savedir.mkdir(parents=True, exist_ok=True)

        fig.savefig(savedir / figname, **save_kwargs)
        plt.close(fig)

    def add_norm(self, levels, cmap):

        return mpl.colors.BoundaryNorm(levels, ncolors=cmap.N, clip=True)

    def get_color_bounds(self):
        """get color bounds from config file"""
        level_range = self.plot_config.get("levels", None)

        if len(level_range) > 3:
            levels = level_range
        else:
            nlevel = int((level_range[1] - level_range[0]) / level_range[2]) + 1
            # levels = np.arange(level_range[0],level_range[1],level_range[2])
            levels = np.linspace(level_range[0], level_range[1], nlevel)

        return levels

    def get_colormap(self, levels):
        """get colors or cmap from config file"""
        # get colormap
        colors = self.plot_config["colors"]

        if len(colors) == 1:
            cmap = plt.get_cmap(colors[0])
        else:
            cmap = mpl.colors.ListedColormap(colors)

        norm = mpl.colors.BoundaryNorm(levels, cmap.N)

        return cmap, norm

    def plot_vertical_section(self, lev, time):

        # create fig and ax
        field_num = len(self.field)
        fig, axlist = self.create_panel_fig_init(field_num)

        # get color bounds
        levels = self.get_color_bounds()
        if self.shortname == "t":
            cbar_ticks = levels[::5]
        else:
            cbar_ticks = levels
        # get colormap
        cmap, norm = self.get_colormap(levels)

        # plot field

        if field_num > 1:

            for i, ax in enumerate(axlist):
                plot = ax.pcolormesh(time, lev, self.field[i], cmap=cmap, norm=norm)

                ax.invert_yaxis()
                ax.set_xlabel("Time (hr)", fontsize=20)
                ax.set_ylabel("Model Level", fontsize=20)
                # add colorbar
                self.add_colorbar(plot, fig, ax, cbar_ticks)

                # add title
                self.add_title(ax, str(i + 1), self.para_val[i])
                ax.tick_params(axis="both", labelsize=20, direction="out")

        else:

            plot = ax.pcolormesh(time, lev, self.field[i], cmap=cmap, norm=norm)

        # save figure
        self.save_fig(fig)

    def plot_time_series(self, times):

        fig, ax = plt.subplots(figsize=[10, 5])

        levels = self.get_color_bounds()
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.field)))

        for i in np.arange(len(self.field)):

            label = f"Uran{i+1}: {self.para_val[i]}"
            ax.plot(
                times,
                self.field[i],
                label=label,
                color=colors[i],
                linewidth="1",
                linestyle="solid",
            )

        ax.set_xlabel("Time (hr)", size=16)
        ax.set_ylabel(f"{self.shortname} ({self.preprocess_config['units']})", size=16)
        ax.spines.top.set_visible(False)
        ax.spines.right.set_visible(False)

        ax.set_xlim(times[0], times[-1])
        # ntimes = [ i for i in range(len(times))]
        # ax.set_xticks(ntimes[::30])
        # ax.set_xticklabels(times[::30])

        ax.set_ylim(levels[0], levels[-1])
        ax.set_yticks(levels)
        ax.set_yticklabels(levels)

        ax.grid(True, color="grey", linewidth=0.6, alpha=0.3)
        ax.legend(loc="lower right", fontsize=8, labelspacing=0.2, title=self.para_name)
        ax.tick_params(axis="both", labelsize=12, direction="out")

        self.save_fig(fig)
