#!/bin/bash

# Initializing virtual environment
echo "Initializing virtual environment..."
pip install virtualenv
cd project_folder || exit
virtualenv habit_tracker_venv
source habit_tracker_venv/bin/activate
if [[ -e habit_tracker_venv ]]
then
  echo "Virtual environment successfully initialized."
else
  echo "Something went wrong."
  exit
fi

# Installing requirements
echo "Installing requirements..."
pip install -r requirements.txt
if [[ -e habit_tracker_venv/lib/python3.9/site-packages/pytest
&& -e habit_tracker_venv/lib/python3.9/site-packages/questionary ]]
then
  echo "Requirements successfully installed."
else
  echo "Something went wrong."
fi