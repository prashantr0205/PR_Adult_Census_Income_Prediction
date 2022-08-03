from setuptools import setup,find_packages
from typing import List

#Declaring Variables for setup functions
PROJECT_NAME="Adult-Census-Income-Prediction"
VERSION="0.0.1"
AUTHOR ="Prashant"
DESCRIPTION= "The Goal is to predict whether a person has an income of more than 50K a year or not."

REQUIREMENT_FILE_NAME="requirements.txt"

HYPHEN_E_DOT = "-e ."
def get_requirements_list()->List[str]:
    """
    Description: This function is going to return list of requirements
    mentioned in requirements.txt file.

    Return: This function is going to return a list  which contains names 
    of libraries mentioned in requirements.txt file.
    """
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        requirement_list = requirement_file.readlines()
        requirement_list = [requirement_name.replace("\n", "") for requirement_name in requirement_list]
        if HYPHEN_E_DOT in requirement_list:
            requirement_list.remove(HYPHEN_E_DOT)
        return requirement_list

setup(
name=PROJECT_NAME,
version=VERSION,
author=AUTHOR,
description=DESCRIPTION,
packages=find_packages(),
install_requires=get_requirements_list()
)