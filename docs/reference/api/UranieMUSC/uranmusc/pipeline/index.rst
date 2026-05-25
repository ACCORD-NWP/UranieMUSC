UranieMUSC.uranmusc.pipeline
============================

.. py:module:: UranieMUSC.uranmusc.pipeline

.. autoapi-nested-parse::

   Module providing a high-level interface for the uranmusc pipeline.

   This module exports key Luigi tasks and parameters used to orchestrate
   the full simulation workflow, from cloning repositories to post-processing.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/UranieMUSC/uranmusc/pipeline/base/index
   /reference/api/UranieMUSC/uranmusc/pipeline/build/index
   /reference/api/UranieMUSC/uranmusc/pipeline/parameters/index
   /reference/api/UranieMUSC/uranmusc/pipeline/post/index
   /reference/api/UranieMUSC/uranmusc/pipeline/pre/index
   /reference/api/UranieMUSC/uranmusc/pipeline/run/index
   /reference/api/UranieMUSC/uranmusc/pipeline/setup_experiment/index
   /reference/api/UranieMUSC/uranmusc/pipeline/setup_musc/index


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.Run


Package Contents
----------------

.. py:class:: Run(*args, **kwargs)

   Bases: :py:obj:`luigi.WrapperTask`


   A wrapper task that runs the entire pipeline from end to end.

   Attributes:
       bin_dir (luigi.Parameter): Directory containing binaries.
       ntasks (luigi.IntParameter): Number of tasks for parallel execution.
       rerun_all (luigi.BoolParameter): Whether to rerun all tasks.
       config (PydanticModelParameter): Path to the configuration file.


   .. py:attribute:: bin_dir


   .. py:attribute:: ntasks


   .. py:attribute:: rerun_all


   .. py:attribute:: config


   .. py:method:: requires()

      Specifies the full pipeline dependencies.

      Yields:
          ConvertLFAToNetCDF: The final task in the pipeline.
