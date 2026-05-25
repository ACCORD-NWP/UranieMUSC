UranieMUSC.uranmusc.log
=======================

.. py:module:: UranieMUSC.uranmusc.log

.. autoapi-nested-parse::

   This module is a hack to replace luigi's normal logging functionality so we can
   use loguru instead



Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.log.original_addHandler


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.log.InterceptHandler


Functions
---------

.. autoapisummary::

   UranieMUSC.uranmusc.log.is_luigi_logging_setup_in_call_stack
   UranieMUSC.uranmusc.log.setup_loguru_logger
   UranieMUSC.uranmusc.log.addHandlerWithNotification
   UranieMUSC.uranmusc.log.setup_luigi_log_interception


Module Contents
---------------

.. py:function:: is_luigi_logging_setup_in_call_stack()

.. py:data:: original_addHandler

.. py:function:: setup_loguru_logger()

.. py:function:: addHandlerWithNotification(self, hdlr)

.. py:class:: InterceptHandler(level=NOTSET)

   Bases: :py:obj:`logging.Handler`


   Intercept standard logging messages toward Loguru sinks.


   .. py:method:: emit(record)

      Do whatever it takes to actually log the specified logging record.

      This version is intended to be implemented by subclasses and so
      raises a NotImplementedError.



.. py:function:: setup_luigi_log_interception(loglevel=logging.INFO)
