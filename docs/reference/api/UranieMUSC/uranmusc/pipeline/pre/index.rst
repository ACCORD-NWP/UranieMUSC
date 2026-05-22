UranieMUSC.uranmusc.pipeline.pre
================================

.. py:module:: UranieMUSC.uranmusc.pipeline.pre


Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.pre.logger


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.pre.CloneRepos


Module Contents
---------------

.. py:data:: logger

.. py:class:: CloneRepos(*args, **kwargs)

   Bases: :py:obj:`uranmusc.pipeline.base.RerunBaseTask`


   A base class for all tasks that should be rerunnable.


   .. py:method:: output()

      The output that this Task produces.

      The output of the Task determines if the Task needs to be run--the task
      is considered finished iff the outputs all exist. Subclasses should
      override this method to return a single :py:class:`Target` or a list of
      :py:class:`Target` instances.

      Implementation note
        If running multiple workers, the output must be a resource that is accessible
        by all workers, such as a DFS or database. Otherwise, workers might compute
        the same output since they don't see the work done by other workers.

      See :ref:`Task.output`



   .. py:method:: run()

      Dummy task to be overriden.

      Serves solely the purpose of making the type checker understand the
      correct type of self.config for all tasks that inherit from BaseTask



