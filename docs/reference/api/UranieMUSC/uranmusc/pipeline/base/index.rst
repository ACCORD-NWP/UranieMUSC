UranieMUSC.uranmusc.pipeline.base
=================================

.. py:module:: UranieMUSC.uranmusc.pipeline.base


Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.base.logger


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.base.BaseTask
   UranieMUSC.uranmusc.pipeline.base.RerunBaseTask


Module Contents
---------------

.. py:data:: logger

.. py:class:: BaseTask(*args, **kwargs)

   Bases: :py:obj:`luigi.Task`


   This is the base class of all Luigi Tasks, the base unit of work in Luigi.

   A Luigi Task describes a unit or work.

   The key methods of a Task, which must be implemented in a subclass are:

   * :py:meth:`run` - the computation done by this task.
   * :py:meth:`requires` - the list of Tasks that this Task depends on.
   * :py:meth:`output` - the output :py:class:`Target` that this Task creates.

   Each :py:class:`~luigi.Parameter` of the Task should be declared as members:

   .. code:: python

       class MyTask(luigi.Task):
           count = luigi.IntParameter()
           second_param = luigi.Parameter()

   In addition to any declared properties and methods, there are a few
   non-declared properties, which are created by the :py:class:`Register`
   metaclass:



   .. py:attribute:: config
      :type:  uranmusc.config_parser.Config


   .. py:method:: run()

      Dummy task to be overriden.

      Serves solely the purpose of making the type checker understand the
      correct type of self.config for all tasks that inherit from BaseTask



.. py:class:: RerunBaseTask(*args, **kwargs)

   Bases: :py:obj:`BaseTask`


   A base class for all tasks that should be rerunnable.


   .. py:attribute:: rerun_task


   .. py:attribute:: rerun_all


   .. py:method:: complete()

      If the task has any outputs, return ``True`` if all outputs exist.
      Otherwise, return ``False``. If --rerun-task or --rerun-all is True,
      return ``False``.
