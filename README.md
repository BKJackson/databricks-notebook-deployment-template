# Databricks notebook deployment template
Python script to utilize the databricks-cli to upload notebook folders while also checking libraries installed on clusters


## Requirements

Python >= 3.6 is required to use this module

databricks-cli has to be installed usint ``pip install databricks-cli``

## Installation
No installation is necessary beyond having python and the databricks cli in your path variable

## Usage
Once the requirements have been met you can use the script to upload folders of notebooks to a databricks workspace. The command to run this script is fairly simple and is as follows

``python <path-to-databricks_search.py> --cluster-name <name of cluster> --source-folder <path-to-source-folder> --destination-folder <absolute-path-of-destination-folder> -p <databricks-cli profile>``

The command includes several paraemeters and they are as follows
1. **--cluster-name**: Name of the cluster that the notebook is to be attached to.
    * required: Yes
    * Default: None
    * Case sensitive: Yes
2. **--source-folder**: Path to the folder containing the databricks notebooks, either relative or absolute.
    * required: Yes
    * Default: None
    * Case sensitive: Yes
3. **--destination-folder**:  Absolute path of the folder in the databricks workspace where the notebooks are to be placed
    * required: Yes
    * Default: None
    * Case sensitive: Yes
4. **--profile**:  databricks-cli profile to use when connecting. This will also define which workspace is being used
    * required: No
    * Default profile: DEFAULT 
    * Case sensitive: Yes
5. **-p**:  Same as --profile

## Setting up databricks-cli profile
Setting up the databricks cli profile can be done fairly easily by utilizing one of the following commands and following the prompts:

Use ``databricks configure --profile <profile-name> --token`` to configure the profile using a token, or ``databricks configure --profile <profile-name>`` to configure using a username and password.
