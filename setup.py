import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="awsiamvault",
    version="0.0.2",
    author="Chris Hodges",
    author_email="chris@humbershoe.co.uk",
    description=("A small helper for getting a secret"
                 "from Vault using IAM role credentials"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cjhodges77/aws-iam-vault",
    packages=['awsiamvault'],
    install_requires=[
        'boto3',
        'hvac'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
)
