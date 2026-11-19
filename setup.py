from setuptools import setup, find_packages
setup(name="erpnext_zimra", version="0.2.0", packages=find_packages(),
      include_package_data=True, zip_safe=False,
      install_requires=["requests>=2.31,<3", "cryptography>=41.0,<46"])
