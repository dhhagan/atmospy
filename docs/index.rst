:html_theme.sidebar_secondary.remove:

atmospy: air quality data visualization
=======================================

.. grid:: 6
   :gutter: 1

   .. grid-item::

      .. image:: example_thumbs/pollution_rose_thumb.png
         :target: ./examples/pollution_rose.html

   .. grid-item::

      .. image:: example_thumbs/dielplot_thumb.png
         :target: ./examples/dielplot.html

   .. grid-item::
      
      .. image:: example_thumbs/regression_thumb.png
         :target: ./examples/regression.html

   .. grid-item::
      
      .. image:: example_thumbs/calendar_by_hour_thumb.png
         :target: ./examples/calendar_by_hour.html

   .. grid-item::
      
      .. image:: example_thumbs/diel_by_weekend_weekday_thumb.png
         :target: ./examples/diel_by_weekend_weekday.html

   .. grid-item::
      
      .. image:: example_thumbs/rose_by_month_thumb.png
         :target: ./examples/rose_by_month.html



.. grid:: 1 1 2 2

   .. grid-item::
      :columns: 12 12 8 8

      *atmospy* is a general-purpose data visualization library for air quality and 
      air sensor data. It is based on `matplotlib <https://matplotlib.org/>`_ and heavily influenced by and 
      dependent on `seaborn <https://seaborn.pydata.org/index.html>`_. It is 
      moderately opionated and the core objective is to provide a way to produce 
      professional graphics for air quality data with a single function call.

      For a more in-depth overview, you can read through the :doc:`tutorial and introductory notes <tutorial>`.
      To get started, visit the :doc:`installation page <installing>` 
      or visit the :doc:`example gallery <examples/index>` to get inspired and see what is 
      easily possible with *atmospy*.

      *atmospy* is open-sourced and is not specific to any sensor or sensor company. Any and all 
      can (and should) use it. To view the source code or report a bug, please visit the 
      `GitHub repository <https://github.com/dhhagan/atmospy>`_.

      .. note::

         This library was recently revamped and released and may contain bugs. Expect frequent updates 
         throughout 2024.

         If you have example datasets that you are interested in donating to be incorporated for general 
         use, please open a GitHub issue and we will be in touch!

   
   .. grid-item-card:: Contents
      :columns: 12 12 4 4
      :class-title: sd-fs-5
      :class-body: sd-pl-4

      .. toctree::
         :maxdepth: 1

         Installing <installing>
         Gallery <examples/index>
         Tutorial <tutorial>
         API <api>

