# Sletning af rykkerspærre på udlignede aftaleindhold

This RPA robot operates in SAP GUI and searches a list of rykkerspærre, a list of open cases and then deletes all rykkerspærre not assigned to an open case.

Most of the robot logic is placed under `robot_framework/sap`.

When the robot is run from OpenOrchestrator the `main.py` file is run which results
in the following:
1. The working directory is changed to where `main.py` is located.
2. A virtual environment is automatically setup with the required packages.
3. The framework is called passing on all arguments needed by [OpenOrchestrator](https://github.com/itk-dev-rpa/OpenOrchestrator).

## Requirements
Minimum python version 3.10

### Linear Flow

The linear framework is used when a robot is just going from A to Z without fetching jobs from an
OpenOrchestrator queue.
The flow of the linear framework is sketched up in the following illustration:

![Linear Flow diagram](Robot-Framework.svg)
