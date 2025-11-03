from setuptools import find_packages,setup
from typing import List

HYPHEN_E_DOT="-e ."
def get_requirements(filepath:str)->list[str]:

    """
    This function will return the list of requirements
    """
    #created an empty list
    requirements=[]

    #now we are going to read this line by line
    with open(filepath,'r') as file_object:
        lines=file_object.readlines()
        requirements=[req.replace("\n","") for req in lines]
        #read what's in the file line by line and append to the requirwmwnts file
         
        ## we will take out -e ;
        if HYPHEN_E_DOT in requirements:
            requirements.remove(HYPHEN_E_DOT)
    return requirements

setup(
    name="networksys",
    version="0.0.0",
    author="Nii Adjei Sowah",
    author_email="niiadjei.sowah68@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
    
    
)


