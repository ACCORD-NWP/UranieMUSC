UranieMUSC.uranmusc.plotting.dataset
====================================

.. py:module:: UranieMUSC.uranmusc.plotting.dataset


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.plotting.dataset.Dataset
   UranieMUSC.uranmusc.plotting.dataset.Uranie


Module Contents
---------------

.. py:class:: Dataset(general_config, field_config, uraniter)

   .. py:attribute:: general_config


   .. py:attribute:: general_case_config


   .. py:attribute:: field_keys_config


   .. py:attribute:: field_preprocess_config


   .. py:attribute:: uraniter


   .. py:attribute:: field
      :value: None



   .. py:property:: filedir


   .. py:method:: lfafiles()

      get Out*lfa files



   .. py:method:: read_netcdf(varname)


   .. py:method:: sum_over_dim(field, dim)

      sum field over dimension dim



.. py:class:: Uranie(general_config)

   .. py:attribute:: general_config


   .. py:method:: read_init_doe()


