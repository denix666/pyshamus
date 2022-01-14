from setuptools import setup, find_packages

setup(name='pyshamus',
      version='0.6',
      description='Clone of old DOS game "SHAMUS"',
      url='https://github.com/denix666/pyshamus',
      author='Denis Salmanovich',
      author_email='denis.salmanovich@gmail.com',
      include_package_data=True,
      license='GPLv3',
      packages=find_packages(),
      package_data={
        '': ['*.ttf', '*.png', '*.mp3', '*.wav', '*.json'],
      },
      requires=[
        'arcade (>=2.6.8)',
        'pygame (>=2.1.2)',
        ],
      zip_safe=False,
      entry_points={
          'console_scripts': ['pyshamus=pyshamus.__main__:main'],
      }
      )
