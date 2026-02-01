"""
Setup.py files are important for packaging and distributing Python projects. It is used by setuptools to define the configuration of your porject. They contain metadata, dependencies,etc about the project and instructions on how to install it.

Any python package that is installed or imported has its own setup file for its metadata, versions etc.

find_packages -> searches ofr folder having "__init__.py" file and considers them as packages. 

-e. -> When we run (pip install -r requirements.txt), python reads all the packages mentioned in req.txt file and as soons as it cooms to (-e.) , it is redirected to setup.py file and this file is now executed where it ignores (-e.) and continues with rest of the installation.

"""


from setuptools import setup, find_packages
from typing import List

def get_requirements(file_path: str) -> List[str]:
    """
    This function will return list of requirements mentioned in requirements.txt file

    """

    try:
        with open('requirements.txt', 'r') as file:
            lines = file.readlines()
            requirements_lst=[]
            for line in lines:
                requirement=line.strip()
                if requirement and requirement!="-e.":
                    requirements_lst.append(requirement)

            
    except FileNotFoundError:
        print("requirements.txt file not found.")

    return requirements_lst

# print(get_requirements('requirements.txt'))

setup(
    name="Network Security Project",
    version="0.0.1",
    author="Aastha Rathore",
    author_email="rathoreaastha1510@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt")

)