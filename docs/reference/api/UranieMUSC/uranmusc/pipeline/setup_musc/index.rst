UranieMUSC.uranmusc.pipeline.setup_musc
=======================================

.. py:module:: UranieMUSC.uranmusc.pipeline.setup_musc

.. autoapi-nested-parse::

   Module for setting up MUSC-specific configurations.

   This module contains Luigi tasks for setting up MUSC run scripts
   and namelists.



Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.setup_musc.logger


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.setup_musc.SetupMusc
   UranieMUSC.uranmusc.pipeline.setup_musc.SetupMuscNamelists


Module Contents
---------------

.. py:data:: logger

.. py:class:: SetupMusc(*args, **kwargs)

   Bases: :py:obj:`uranmusc.pipeline.base.RerunBaseTask`


   Luigi task to set up MUSC environment.

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
          list: A list of luigi.LocalTarget objects for the MUSC setup files.



   .. py:method:: run()

      Executes the MUSC setup.

      Runs the Harmonie MUSC setup script to prepare the experiment directory.



.. py:class:: SetupMuscNamelists(*args, **kwargs)

   Bases: :py:obj:`uranmusc.pipeline.base.RerunBaseTask`


   Luigi task to set up MUSC namelists.

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
          list: A list of luigi.LocalTarget objects for the generated namelists.



   .. py:method:: run()

      Executes the MUSC namelist setup.

      Either copies existing namelists or generates them via a shell script.



