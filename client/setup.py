from setuptools import setup, find_packages

setup(name="message_client_march",
      version="0.1",
      description="mess_client",
      author="Xemur0",
      author_email="aleks.prfnk@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )