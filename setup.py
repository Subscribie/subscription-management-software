import io

from setuptools import find_packages
from setuptools import setup

with io.open("README.md", "rt", encoding="utf8") as f:
  readme = f.read()

setup(
  name="Subscription Management Software SSOT",
  version="0.01",
  url="https://github.com/Subscribie/subscription-management-software",
  author="Christopher Simpson",
  author_email="chris@karmacomputing.co.uk",
  description="Subscription management software",
  long_description=readme,
  classifiers=["Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
  ],
  packages=find_packages("src"),
  package_dir={"": "src"},
  include_package_data=True,
  install_requires=["gocardless_pro"]
)
