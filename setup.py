from setuptools import setup, find_packages

requirements = [
    'python-dotenv',
]

setup(name='eve-config',
      version='0.1.2',
      description='Eve framework configuration extension',
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='WhoisBuster',
      author_email='github@whoisbuster.com',
      url='https://www.whoisbuster.com/',
      keywords='web wsgi bfg eve rest',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requirements)
