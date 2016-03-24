"""Setup.py for Simple Scraper app."""
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()


requires = [
    'bs4',
    'requests',
]

test_require = ['pytest', 'pytest-watch', 'pytest-cov', 'tox', 'bs4']
dev_requires = ['ipython']

setup(name='basic-scraper',
      version='0.0',
      description='basic-scraper',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
      ],
      author='Will Weatherford',
      author_email='weatherford.william@gmail.com',
      url='',
      keywords='scraper',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='basic_scraper',
      install_requires=requires,
      extras_require={
          'test': test_require,
          'dev': dev_requires,
      },
      entry_points="""\
      """,
      )
