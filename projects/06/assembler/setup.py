import setuptools


setuptools.setup(
    name="assembler",
    version="0.0.1",
    author="Sam Davis",
    description="An assembler for the Hack assembly language",
    packages=setuptools.find_packages(),
    entry_points = {
        "console_scripts": [
            "hack_assembler = assembler.main:main"
        ]
    }
)
