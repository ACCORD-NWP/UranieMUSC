UranieMUSC.uranmusc.pipeline.run
================================

.. py:module:: UranieMUSC.uranmusc.pipeline.run

.. autoapi-nested-parse::

   Module for running URANIE and MUSC simulations.

   This module contains Luigi tasks for executing the URANIE design of
   experiment and the subsequent MUSC simulation runs.



Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.run.logger


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.run.RunUranie
   UranieMUSC.uranmusc.pipeline.run.RunMusc


Module Contents
---------------

.. py:data:: logger

.. py:class:: RunUranie(*args, **kwargs)

   Bases: :py:obj:`uranmusc.pipeline.base.RerunBaseTask`


   Luigi task to run the URANIE design of experiment.

   Attributes:
       bin_dir (luigi.Parameter): Directory containing binaries.


   .. py:attribute:: bin_dir


   .. py:method:: requires()

      Specifies the dependencies for this task.

      Returns:
          list: A list of tasks that must be completed before this task.



   .. py:method:: output()

      Specifies the output targets for this task.

      Returns:
          list: A list of luigi.LocalTarget objects representing the output files.



   .. py:method:: run()

      Executes the URANIE design of experiment.

      Prepares the URANIE namelist by injecting DOE variables and then
      runs the URANIE python script via subprocess.



.. py:class:: RunMusc(*args, **kwargs)

   Bases: :py:obj:`uranmusc.pipeline.base.RerunBaseTask`


   Luigi task to run the MUSC simulation.

   Attributes:
       bin_dir (luigi.Parameter): Directory containing binaries.
       ntasks (luigi.IntParameter): Number of tasks to run in parallel via Slurm.


   .. py:attribute:: bin_dir


   .. py:attribute:: ntasks


   .. py:method:: requires()

      Specifies the dependencies for this task.

      Returns:
          list: A list of tasks that must be completed before this task.



   .. py:method:: output()

      Specifies the output targets for this task.

      Returns:
          list: A list of luigi.LocalTarget objects representing the first
              LFA file of each expected output directory.



   .. py:method:: run()

      Executes the MUSC simulation.

      Prepares MUSC namelists by copying and symlinking files, generates a
      Slurm batch script, and submits it using `sbatch`.



