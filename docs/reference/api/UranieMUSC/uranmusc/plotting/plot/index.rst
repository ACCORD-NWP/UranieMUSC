UranieMUSC.uranmusc.plotting.plot
=================================

.. py:module:: UranieMUSC.uranmusc.plotting.plot


Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.plotting.plot.font_dirs
   UranieMUSC.uranmusc.plotting.plot.font_files


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.plotting.plot.Plot


Module Contents
---------------

.. py:data:: font_dirs
   :value: '/perm/iczx/EPyGrAM/mscorefonts-0.0.1-3'


.. py:data:: font_files

.. py:class:: Plot(general_config, field_config, field, shortname)

   .. py:attribute:: general_config


   .. py:attribute:: plot_config


   .. py:attribute:: preprocess_config


   .. py:attribute:: field


   .. py:attribute:: shortname


   .. py:method:: create_panel_fig_init(fig_num)


   .. py:method:: add_title(ax, left_label, center_label)

      add title



   .. py:method:: add_colorbar(plot, fig, ax, ticks)

      add colorbar



   .. py:method:: save_fig(fig)

      save figure



   .. py:method:: add_norm(levels, cmap)


   .. py:method:: get_color_bounds()

      get color bounds from config file



   .. py:method:: get_colormap(levels)

      get colors or cmap from config file



   .. py:method:: plot_vertical_section(lev, time)


   .. py:method:: plot_time_series(times)


