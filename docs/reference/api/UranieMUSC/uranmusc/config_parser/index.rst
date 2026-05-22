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
   UranieMUSC.uranmusc.config_parser.DataFilesConfig
   UranieMUSC.uranmusc.config_parser.VariablesConfig
   UranieMUSC.uranmusc.config_parser.DesignOfExperimentConfig
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


   .. py:attribute:: bin_dir
      :type:  Optional[pathlib.Path]
      :value: None



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


   .. py:attribute:: design_of_experiment
      :type:  DesignOfExperimentConfig


.. py:class:: DataFilesConfig(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Configuration for data files used in a MUSC experiment.


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



   .. py:attribute:: dataserver
      :type:  pathlib.Path


   .. py:attribute:: namelist_dir
      :type:  Optional[pathlib.Path]
      :value: None



   .. py:attribute:: namelist_template
      :type:  str


.. py:class:: VariablesConfig(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Configuration for the input variables and their namelist flags.


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



   .. py:attribute:: inputs
      :type:  List[str]


   .. py:attribute:: namelist_flags
      :type:  List[str]


   .. py:method:: check_namelist_flags(value)

      Check that all namelist flags start and end with '@'.

      Args:
          value (List[str]): List of namelist flags

      Raises:
          ValueError: If any namelist flag does not start and end with '@'

      Returns:
          List[str]: List of namelist flags



.. py:class:: DesignOfExperimentConfig(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Design of experiment configuration.


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



   .. py:attribute:: type
      :type:  Literal['morris_sensitivity', 'sampling']


   .. py:attribute:: data_files
      :type:  DataFilesConfig


   .. py:attribute:: variables
      :type:  VariablesConfig


   .. py:method:: to_yaml(output_path: pathlib.Path, musc_id: str)


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



   .. py:property:: project_dir
      :type: pathlib.Path



   .. py:property:: namelist_atm
      :type: pathlib.Path



   .. py:property:: namelist_sfx
      :type: pathlib.Path



