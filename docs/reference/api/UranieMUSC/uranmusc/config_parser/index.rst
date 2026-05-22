UranieMUSC.uranmusc.config_parser
=================================

.. py:module:: UranieMUSC.uranmusc.config_parser

.. autoapi-nested-parse::

   Configuration parser for UranMusc using pydantic.



Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.config_parser.GeneralConfig
   UranieMUSC.uranmusc.config_parser.ExperimentConfig
   UranieMUSC.uranmusc.config_parser.GitRepositoryConfig
   UranieMUSC.uranmusc.config_parser.GitRepositoriesConfig
   UranieMUSC.uranmusc.config_parser.Config


Module Contents
---------------

.. py:class:: GeneralConfig(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   General configuration.


   .. py:attribute:: ura_env
      :type:  pathlib.Path


   .. py:attribute:: musc_data_dir
      :type:  pathlib.Path


   .. py:attribute:: hm_home
      :type:  pathlib.Path


   .. py:attribute:: scratch_hm_home
      :type:  pathlib.Path


   .. py:attribute:: grp
      :type:  Optional[str]
      :value: None



.. py:class:: ExperimentConfig(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Experiment configuration.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: fc_length
      :type:  int


   .. py:attribute:: musc_id
      :type:  str


   .. py:attribute:: musc_case
      :type:  str


   .. py:attribute:: ura_init
      :type:  pathlib.Path


   .. py:attribute:: ura_init_namelist
      :type:  pathlib.Path


.. py:class:: GitRepositoryConfig(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Git repository configuration.


   .. py:attribute:: repo
      :type:  pathlib.Path


   .. py:attribute:: url
      :type:  str


   .. py:attribute:: branch
      :type:  str


.. py:class:: GitRepositoriesConfig(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Git repositories configuration.


   .. py:attribute:: harmonie
      :type:  GitRepositoryConfig


   .. py:attribute:: ddhtoolbox
      :type:  GitRepositoryConfig


   .. py:attribute:: musc_data
      :type:  GitRepositoryConfig


.. py:class:: Config(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Main configuration.


   .. py:attribute:: general
      :type:  GeneralConfig


   .. py:attribute:: experiment
      :type:  ExperimentConfig


   .. py:attribute:: git_repos
      :type:  GitRepositoriesConfig


   .. py:method:: create_dirs()


   .. py:property:: home_exp_dir
      :type: pathlib.Path



   .. py:property:: scratch_exp_dir
      :type: pathlib.Path



   .. py:property:: uranie_dir
      :type: pathlib.Path



   .. py:property:: output_dir
      :type: pathlib.Path



