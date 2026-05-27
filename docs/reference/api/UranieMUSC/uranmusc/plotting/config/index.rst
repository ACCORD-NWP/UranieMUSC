UranieMUSC.uranmusc.plotting.config
===================================

.. py:module:: UranieMUSC.uranmusc.plotting.config


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.plotting.config.Config


Module Contents
---------------

.. py:class:: Config(config_file, field: str)

   Load config.toml and retrieve any config related to a given field


   .. py:attribute:: config_path


   .. py:attribute:: field


   .. py:attribute:: config
      :value: None



   .. py:method:: load_config()

      Load config.toml file



   .. py:method:: get_section_config(section='general', sub_path: Optional[str] = None) -> dict

      Return section config information



   .. py:method:: get_field_config(sub_path: Optional[str] = None) -> dict

      Return config information for field
