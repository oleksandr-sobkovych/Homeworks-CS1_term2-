import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Oleksandr Sobkovych",
    version="1.0",
    author="Oleksandr Sobkovych",
    author_email="oleksandr.sobkovych@gmail.com",
    description="A package for classifying mazes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Alex-quickcoder/Homeworks-CS1_term2-",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)