from setuptools import setup, find_packages

setup(name="messenger_server_march",
      version="0.1",
      description="messenger_server",
      author="Xemur0",
      author_email="aleks.prfnk@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )