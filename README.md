atmospy
=======

Python library for the atmospheric sciences

    import atmospy
    import atmospy.io

    df = atmospy.AlphasenseLoader()
    df.load(p, "X102 PM*.csv")

    a = atmospy.AlphasenseOPCN2(dN = df.hist.resample('10min').mean())

## Running Unittests

    coverage run --source atmospy setup.py test

    coverage report -m
