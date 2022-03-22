from setuptools import setup, find_packages

with open("README.md", "r") as f:
    ld = f.read()
with open("LICENSE.md", "r") as f:
    lc = f.read()

setup(
    name="knowledge-clustering",
    version="0.2.1",
    author="Rémi Morvan",
    author_email="remi@morvan.xyz",
    description="Automated notion clustering for the knowledge LaTeX package",
    long_description=ld,
    long_description_content_type="text/markdown",
    license=lc,
    url="https://github.com/remimorvan/knowledge-clustering",
    project_urls={
        "Tracker": "https://github.com/remimorvan/knowledge-clustering/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="knowledge latex clustering",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Click", "nltk"],
    entry_points={
        "console_scripts": [
            "knowledge = knowledge_clustering.scripts.app:cli",
        ],
    },
)
