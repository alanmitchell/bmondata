# bmondata
Allows easy access to sensor data residing on a [BMON Server](https://github.com/alanmitchell/bmon).

This package provides a wrapper around the the BMON API, version 2.  It allows retrieval
of key data stored in the BMON database, including sensor readings, sensor metadata, building
information, and organization information.  It is not comprehensive as some BMON information is
not available.  It also allows for storage of new sensor readings in a BMON
sensor reading database.

Usage examples are [shown here](http://htmlpreview.github.io/?https://github.com/alanmitchell/bmondata/blob/master/examples/usage_examples.html).
The docstring for each method gives additional information.

Install with pip:

    pip install --upgrade bmondata

This package is only compatible with BMON Servers running the BMON software version
equal to or greater than:  Mon Jul 29 16:06:14 2019 -0800 (shown on the footer of the 
BMON Graphs/Reports page.)
