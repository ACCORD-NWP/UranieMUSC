UranieMUSC.uranmusc.pipeline.setup_experiment
=============================================

.. py:module:: UranieMUSC.uranmusc.pipeline.setup_experiment

.. autoapi-nested-parse::

   Module for setting up the experiment environment.

   This module contains Luigi tasks for cleaning and configuring
   the experiment directory.



Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.setup_experiment.logger


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.setup_experiment.SetupExperiment


Module Contents
---------------

.. py:data:: logger

.. py:class:: SetupExperiment(*args, **kwargs)

   Bases: :py:obj:`uranmusc.pipeline.base.RerunBaseTask`


   Luigi task to set up the experiment environment.

   Attributes:
       config (PydanticModelParameter): The experiment configuration.


   .. py:method:: requires()

      Specifies the dependencies for this task.

      Returns:
          list: A list of tasks that must be completed before this task.



   .. py:method:: output()

      Specifies the output target for this task.

      Returns:
          luigi.LocalTarget: A target file indicating the experiment is set up.



   .. py:method:: run()

      Executes the experiment setup.

      Cleans the experiment directory by removing non-essential directories,
      and then runs the Harmonie setup command.



