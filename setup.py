import os

from setuptools import find_packages, setup

base_dir = os.path.dirname(os.path.abspath(__file__))
tests_require = [
    "parameterized==0.8.1",
]


def get_long_description():
    readme_path = os.path.join(base_dir, "README.md")
    with open(readme_path, encoding="utf-8") as readme_file:
        return readme_file.read()


def get_project_version():
    version = {}
    with open(os.path.join(base_dir, "yimt", "version.py"), encoding="utf-8") as fp:
        exec(fp.read(), version)
    return version


version = get_project_version()
tf_version_requirement = ">=%s,<%s" % (
    version["INCLUSIVE_MIN_TF_VERSION"],
    version["EXCLUSIVE_MAX_TF_VERSION"],
)


setup(
    name="yimt",
    version=version["__version__"],
    license="MIT",
    description="Neural machine translation using TensorFlow",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="LiuXiaofeng",
    author_email="kiddenliu@sina.com",
    url="https://github.com/hlp-ai",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    project_urls={
        "Source": "https://github.com/hlp-ai/mt-core",
    },
    keywords="tensorflow yimt nmt neural machine translation",
    python_requires=">=3.6",
    install_requires=[
        "ctranslate2>=2.14.0,<3",
        "pyonmttok>=1.29.0,<2",
        "pyyaml>=5.3,<7",
        "rouge>=1.0,<2",
        "sacrebleu>=1.5.0,<2.1",
        "tensorflow-addons>=0.14,<0.17",
        "sentencepiece>=0.1.96",
    ],
    extras_require={
        "tensorflow": [
            "tensorflow" + tf_version_requirement,
            "tensorflow-text" + tf_version_requirement,
        ],
        "tests": tests_require,
    },
    tests_require=tests_require,
    packages=find_packages(exclude=["bin", "*.tests"]),
)
