try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = '0.1.0'

setup(
    name = 'atmospy',
    version = __version__,
    packages = ['atmospy'],
    description = 'Python libary for the atmospheric sciences',
    author = 'David H Hagan',
    author_email = 'david@davidhhagan.com',
    license = 'MIT',
    url = 'https://github.com/dhhagan/atmospy',
    keywords = ['atmospheric chemistry'],
    test_suite = 'tests',
    install_requires = [
        'pandas',
        'numpy'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Topic :: Scientific/Engineering :: Atmospheric Science',
		'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
