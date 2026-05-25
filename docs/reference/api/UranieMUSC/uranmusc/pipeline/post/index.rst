UranieMUSC.uranmusc.pipeline.post
=================================

.. py:module:: UranieMUSC.uranmusc.pipeline.post

.. autoapi-nested-parse::

   Module for post-processing Luigi tasks.

   This module contains Luigi tasks for converting LFA output files
   to NetCDF format.



Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.post.logger


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.post.ConvertLFAToNetCDF


Module Contents
---------------

.. py:data:: logger

.. py:class:: ConvertLFAToNetCDF(*args, **kwargs)

   Bases: :py:obj:`uranmusc.pipeline.run.RerunBaseTask`


   Luigi task to convert LFA files to NetCDF.

   Attributes:
       bin_dir (luigi.Parameter): Directory containing binaries.
       ntasks (luigi.IntParameter): Number of tasks for parallel execution via
           Slurm.


   .. py:attribute:: bin_dir


   .. py:attribute:: ntasks


   .. py:method:: requires()

      Specifies the dependencies for this task.

      Returns:
          list: A list of tasks that must be completed before this task.



   .. py:method:: output()

      Specifies the output targets for this task.

      Returns:
          list: A list of luigi.LocalTarget objects for each expected NetCDF file.



   .. py:method:: run()

      Executes the conversion from LFA to NetCDF.

      Prepares the conversion environment by copying configuration files,
      generates a Slurm batch script, and submits it via `sbatch`.



