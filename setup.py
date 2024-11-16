from setuptools import setup, find_packages

# Read requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ra-gateway",
    version="0.1.0",
    packages=find_packages(),  # This will find src/ and any other packages
    install_requires=requirements,
)