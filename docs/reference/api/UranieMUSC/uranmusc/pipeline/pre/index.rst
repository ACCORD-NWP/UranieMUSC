UranieMUSC.uranmusc.pipeline.pre
================================

.. py:module:: UranieMUSC.uranmusc.pipeline.pre

.. autoapi-nested-parse::

   Module for preliminary pipeline tasks.

   This module contains Luigi tasks for cloning required repositories.



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


   Luigi task to clone necessary repositories.
       


   .. py:method:: output()

      Specifies the output targets for this task.

      Returns:
          list: A list of luigi.LocalTarget objects for each repository's .git directory.



   .. py:method:: run()

      Executes the cloning of repositories.

      For each repository in the configuration, it removes any existing
      directory and then performs a git clone with submodules.



