.. _installing:

.. currentmodule:: atmospy

Installing and getting started
------------------------------

Official `atmospy` releases can be installed directly from PyPi::

    pip install atmospy

You can also install prereleases directly from PyPi::

    pip install --pre atmospy

If you'd like to install from a specific GitHub branch or release, you can do that as well::

    pip install git+https://github.com/dhhagan/atmospy.git@<tag>

Dependencies
~~~~~~~~~~~~

Supported Python versions
^^^^^^^^^^^^^^^^^^^^^^^^^

- Python3.8 - Python3.11 are currently supported 

Mandatory Dependencies
^^^^^^^^^^^^^^^^^^^^^^

- `numpy <https://numpy.org>`__
- `pandas <https://pandas.pydata.org>`__
- `seaborn <https://seaborn.pydata.org>`__
- `matplotlib <https://matplotlib.org>`__
- `scipy <https://scipy.org>`__

For allowed version of each library, please check out the `pyproject.toml` file.

Quickstart
~~~~~~~~~~

Once you have `atmospy` installed, you should have everything you need to get up and running. The 
library includes several example datasets that can be used to play around with the figures and 
to better understand the data format(s) required if you're new to pandas or Python. To use an 
example dataset, load as follows::

    import atmospy

    df = atmospy.load_dataset("air-sensors-met")
    atmospy.pollutionroseplot(data=df, ws="ws", wd="wd", pollutant="pm1")


Debugging install issues
~~~~~~~~~~~~~~~~~~~~~~~~

If you are having trouble installing `atmospy`, it is likely related to 
dependencies and speecific versions. Please feel free to open an issue 
on the GitHub repsository and I will try to help you work through it. Please follow 
the instructions below for Getting Help.


Getting help
~~~~~~~~~~~~

If you think you've encountered a bug, please report it on the `GitHub issue tracker <https://github.com/dhhagan/atmospy/issues>`. Please 
include the following information when you do:

- a reproducible example that demonstrates the problem (use an example dataset where possible)
- the output that you see (e.g., screenshot, figure) if it is related to the figure itself
- the full, formatted traceback if there is a code error
- the specific versions of the key dependencies (you can get these by running `pip list`)
- the operating system of the machine you are using

If you provide an easy-to-reproduce example, I can work quickly to address it.