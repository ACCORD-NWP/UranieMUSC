UranieMUSC.uranmusc.ecflow_handles
==================================

.. py:module:: UranieMUSC.uranmusc.ecflow_handles


Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.ecflow_handles.COMPLETE_STATUS
   UranieMUSC.uranmusc.ecflow_handles.ABORTED_STATUS


Functions
---------

.. autoapisummary::

   UranieMUSC.uranmusc.ecflow_handles.await_ecflow_node_to_complete


Module Contents
---------------

.. py:data:: COMPLETE_STATUS
   :value: 'complete'


.. py:data:: ABORTED_STATUS
   :value: 'aborted'


.. py:function:: await_ecflow_node_to_complete(node_path: str, delay: int = 60) -> None

   Await an ecflow node to complete. If the node is aborted, raises an error.
