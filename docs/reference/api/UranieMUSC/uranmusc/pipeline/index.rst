UranieMUSC.uranmusc.pipeline
============================

.. py:module:: UranieMUSC.uranmusc.pipeline


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


   Use for tasks that only wrap other tasks and that by definition are done if all their requirements exist.


   .. py:attribute:: bin_dir


   .. py:attribute:: ntasks


   .. py:attribute:: rerun_all


   .. py:attribute:: config


   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



