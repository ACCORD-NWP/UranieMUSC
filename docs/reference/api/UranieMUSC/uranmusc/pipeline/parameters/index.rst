UranieMUSC.uranmusc.pipeline.parameters
=======================================

.. py:module:: UranieMUSC.uranmusc.pipeline.parameters


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.parameters.PydanticModelParameter


Functions
---------

.. autoapisummary::

   UranieMUSC.uranmusc.pipeline.parameters.load_config


Module Contents
---------------

.. py:function:: load_config(path_: str)

.. py:class:: PydanticModelParameter(default: Optional[str] = None, **kwargs)

   Bases: :py:obj:`luigi.Parameter`


   Parameter whose value is a ``str``, and a base class for other parameter types.

   Parameters are objects set on the Task class level to make it possible to parameterize tasks.
   For instance:

   .. code:: python

       class MyTask(luigi.Task):
           foo = luigi.Parameter()

       class RequiringTask(luigi.Task):
           def requires(self):
               return MyTask(foo="hello")

           def run(self):
               print(self.requires().foo)  # prints "hello"

   This makes it possible to instantiate multiple tasks, eg ``MyTask(foo='bar')`` and
   ``MyTask(foo='baz')``. The task will then have the ``foo`` attribute set appropriately.

   When a task is instantiated, it will first use any argument as the value of the parameter, eg.
   if you instantiate ``a = TaskA(x=44)`` then ``a.x == 44``. When the value is not provided, the
   value  will be resolved in this order of falling priority:

       * Any value provided on the command line:

         - To the root task (eg. ``--param xyz``)

         - Then to the class, using the qualified task name syntax (eg. ``--TaskA-param xyz``).

       * With ``[TASK_NAME]>PARAM_NAME: <serialized value>`` syntax. See :ref:`ParamConfigIngestion`

       * Any default value set using the ``default`` flag.

   Parameter objects may be reused, but you must then set the ``positional=False`` flag.


   .. py:method:: parse(x: str) -> uranmusc.config_parser.Config

      Parse an individual value from the input.

      The default implementation is the identity function, but subclasses should override
      this method for specialized parsing.

      :param str x: the value to parse.
      :return: the parsed value.



   .. py:method:: serialize(x: pydantic.BaseModel | str) -> str

      Opposite of :py:meth:`parse`.

      Converts the value ``x`` to a string.

      :param x: the value to serialize.
