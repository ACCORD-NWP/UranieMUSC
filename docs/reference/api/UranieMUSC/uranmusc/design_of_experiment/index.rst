UranieMUSC.uranmusc.design_of_experiment
========================================

.. py:module:: UranieMUSC.uranmusc.design_of_experiment


Attributes
----------

.. autoapisummary::

   UranieMUSC.uranmusc.design_of_experiment.parser


Classes
-------

.. autoapisummary::

   UranieMUSC.uranmusc.design_of_experiment.DOEStrategy
   UranieMUSC.uranmusc.design_of_experiment.SamplingDOE
   UranieMUSC.uranmusc.design_of_experiment.MorrisSensitivityDOE
   UranieMUSC.uranmusc.design_of_experiment.DOEFactory


Functions
---------

.. autoapisummary::

   UranieMUSC.uranmusc.design_of_experiment.parse_doe_config
   UranieMUSC.uranmusc.design_of_experiment.run_doe


Module Contents
---------------

.. py:function:: parse_doe_config(doe_config)

   Parse DOE configuration from dict and return pydantic model.

   Args:
       doe_config: Dict containing the design of experiment configuration

   Returns:
       DesignOfExperimentConfig pydantic model


.. py:class:: DOEStrategy

   Bases: :py:obj:`abc.ABC`


   Base class for Design of Experiment strategies.


   .. py:method:: get_required_keys()
      :abstractmethod:


      Return list of required configuration keys for this DOE type.



   .. py:method:: create_sampler(ds, config, dummy_model=None)
      :abstractmethod:


      Create and return the appropriate sampler for this DOE type.

      Args:
          ds: URANIE DataServer
          config: DesignOfExperimentConfig pydantic model
          dummy_model: Optional dummy model for strategies that need it



   .. py:method:: validate_settings(config)
      :abstractmethod:


      Validate that all required settings are present.

      Args:
          config: DesignOfExperimentConfig pydantic model



.. py:class:: SamplingDOE

   Bases: :py:obj:`DOEStrategy`


   Traditional sampling-based Design of Experiment using TSampling.


   .. py:method:: get_required_keys()

      Return list of required configuration keys for this DOE type.



   .. py:method:: validate_settings(config)

      Validate that all required settings are present.

      Args:
          config: DesignOfExperimentConfig pydantic model



   .. py:method:: create_sampler(ds, config, dummy_model=None)

      Create and return the appropriate sampler for this DOE type.

      Args:
          ds: URANIE DataServer
          config: DesignOfExperimentConfig pydantic model
          dummy_model: Optional dummy model for strategies that need it



.. py:class:: MorrisSensitivityDOE

   Bases: :py:obj:`DOEStrategy`


   Morris sensitivity analysis Design of Experiment using TMorris.


   .. py:method:: get_required_keys()

      Return list of required configuration keys for this DOE type.



   .. py:method:: validate_settings(config)

      Validate that all required settings are present.

      Args:
          config: DesignOfExperimentConfig pydantic model



   .. py:method:: create_sampler(ds, config, dummy_model=None)

      Create and return the appropriate sampler for this DOE type.

      Args:
          ds: URANIE DataServer
          config: DesignOfExperimentConfig pydantic model
          dummy_model: Optional dummy model for strategies that need it



.. py:class:: DOEFactory

   Factory for creating appropriate DOE strategy based on configuration.


   .. py:method:: register_strategy(name, strategy_class)
      :classmethod:


      Register a new DOE strategy.



   .. py:method:: create_strategy(doe_type)
      :classmethod:


      Create a DOE strategy instance based on the type.



   .. py:method:: list_strategies()
      :classmethod:


      List all available DOE strategies.



.. py:function:: run_doe(doe_config: pathlib.Path, output_dir: pathlib.Path, namelist_dir=None)

   Main function to run Design of Experiment.

   Args:
       doe_config: Path to YAML file with DOE configuration
       output_dir: Directory to export the dataserver
       namelist_dir: Directory containing the namelist template (optional, inferred from config if not provided)


.. py:data:: parser

