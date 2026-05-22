UranieMUSC.uranmusc.tasks
=========================

.. py:module:: UranieMUSC.uranmusc.tasks


Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.tasks.logger
   UranieMUSC.uranmusc.tasks.config_dict


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.tasks.RerunBaseTask
   UranieMUSC.uranmusc.tasks.CloneRepos
   UranieMUSC.uranmusc.tasks.SetupExperiment
   UranieMUSC.uranmusc.tasks.BuildExperiment
   UranieMUSC.uranmusc.tasks.SetupMusc
   UranieMUSC.uranmusc.tasks.RunUranie
   UranieMUSC.uranmusc.tasks.RunMusc
   UranieMUSC.uranmusc.tasks.BuildDDH
   UranieMUSC.uranmusc.tasks.ConvertLFAToNetCDF
   UranieMUSC.uranmusc.tasks.Run


Module Contents
---------------

.. py:data:: logger

.. py:data:: config_dict

.. py:class:: RerunBaseTask(*args, **kwargs)

   Bases: :py:obj:`luigi.Task`


   A base class for all tasks that should be rerunnable.


   .. py:attribute:: rerun


   .. py:attribute:: rerun_all


   .. py:method:: complete()

      If the task has any outputs, return ``True`` if all outputs exist.
      Otherwise, return ``False``. If --rerun is True, return ``False``.



.. py:class:: CloneRepos(*args, **kwargs)

   Bases: :py:obj:`RerunBaseTask`


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

      The task run method, to be overridden in a subclass.

      See :ref:`Task.run`



.. py:class:: SetupExperiment(*args, **kwargs)

   Bases: :py:obj:`RerunBaseTask`


   A base class for all tasks that should be rerunnable.


   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



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

      The task run method, to be overridden in a subclass.

      See :ref:`Task.run`



.. py:class:: BuildExperiment(*args, **kwargs)

   Bases: :py:obj:`RerunBaseTask`


   A base class for all tasks that should be rerunnable.


   .. py:attribute:: bin_dir


   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



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

      The task run method, to be overridden in a subclass.

      See :ref:`Task.run`



.. py:class:: SetupMusc(*args, **kwargs)

   Bases: :py:obj:`RerunBaseTask`


   A base class for all tasks that should be rerunnable.


   .. py:attribute:: bin_dir


   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



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

      Build the experiment.



.. py:class:: RunUranie(*args, **kwargs)

   Bases: :py:obj:`RerunBaseTask`


   A base class for all tasks that should be rerunnable.


   .. py:attribute:: bin_dir


   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



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

      The task run method, to be overridden in a subclass.

      See :ref:`Task.run`



.. py:class:: RunMusc(*args, **kwargs)

   Bases: :py:obj:`RerunBaseTask`


   A base class for all tasks that should be rerunnable.


   .. py:attribute:: bin_dir


   .. py:attribute:: ntasks


   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



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



   .. py:method:: complete()

      If the task has any outputs, return ``True`` if all outputs exist.
      Otherwise, return ``False``. If --rerun is True, return ``False``.



   .. py:method:: run()

      The task run method, to be overridden in a subclass.

      See :ref:`Task.run`



.. py:class:: BuildDDH(*args, **kwargs)

   Bases: :py:obj:`RerunBaseTask`


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



   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



   .. py:method:: run()

      The task run method, to be overridden in a subclass.

      See :ref:`Task.run`



.. py:class:: ConvertLFAToNetCDF(*args, **kwargs)

   Bases: :py:obj:`RerunBaseTask`


   A base class for all tasks that should be rerunnable.


   .. py:attribute:: bin_dir


   .. py:attribute:: ntasks


   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



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

      The task run method, to be overridden in a subclass.

      See :ref:`Task.run`



.. py:class:: Run(*args, **kwargs)

   Bases: :py:obj:`luigi.WrapperTask`


   Use for tasks that only wrap other tasks and that by definition are done if all their requirements exist.


   .. py:attribute:: bin_dir


   .. py:attribute:: ntasks


   .. py:attribute:: rerun_all


   .. py:method:: requires()

      The Tasks that this Task depends on.

      A Task will only run if all of the Tasks that it requires are completed.
      If your Task does not require any other Tasks, then you don't need to
      override this method. Otherwise, a subclass can override this method
      to return a single Task, a list of Task instances, or a dict whose
      values are Task instances.

      See :ref:`Task.requires`



