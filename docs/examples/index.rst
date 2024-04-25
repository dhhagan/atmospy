
:html_theme.sidebar_secondary.remove:

.. raw:: html

    <style type="text/css">
    .thumb {
        position: relative;
        float: left;
        width: 180px;
        height: 180px;
        margin: 0;
    }

    .thumb img {
        position: absolute;
        display: inline;
        left: 0;
        width: 170px;
        height: 170px;
        opacity:1.0;
        filter:alpha(opacity=100); /* For IE8 and earlier */
    }

    .thumb:hover img {
        -webkit-filter: blur(3px);
        -moz-filter: blur(3px);
        -o-filter: blur(3px);
        -ms-filter: blur(3px);
        filter: blur(3px);
        opacity:1.0;
        filter:alpha(opacity=100); /* For IE8 and earlier */
    }

    .thumb span {
        position: absolute;
        display: inline;
        left: 0;
        width: 170px;
        height: 170px;
        background: #000;
        color: #fff;
        visibility: hidden;
        opacity: 0;
        z-index: 100;
    }

    .thumb p {
        position: absolute;
        top: 45%;
        width: 170px;
        font-size: 110%;
        color: #fff;
    }

    .thumb:hover span {
        visibility: visible;
        opacity: .4;
    }

    .caption {
        position: absolute;
        width: 180px;
        top: 170px;
        text-align: center !important;
    }
    </style>

.. _example_gallery:

Example gallery
===============



.. toctree::
   :hidden:

   ./calendar_by_day

   ./calendar_by_hour

   ./dielplot

   ./pollution_rose

   ./regression





.. raw:: html

    <div class='thumb align-center'>
    <a href=./calendar_by_day.html>
    <img src=../_static/calendar_by_day_thumb.png>
    <span class='thumb-label'>
    <p>calendarplot</p>
    </span>
    </a>
    </div>



.. raw:: html

    <div class='thumb align-center'>
    <a href=./calendar_by_hour.html>
    <img src=../_static/calendar_by_hour_thumb.png>
    <span class='thumb-label'>
    <p>calendarplot</p>
    </span>
    </a>
    </div>



.. raw:: html

    <div class='thumb align-center'>
    <a href=./dielplot.html>
    <img src=../_static/dielplot_thumb.png>
    <span class='thumb-label'>
    <p>dielplot</p>
    </span>
    </a>
    </div>



.. raw:: html

    <div class='thumb align-center'>
    <a href=./pollution_rose.html>
    <img src=../_static/pollution_rose_thumb.png>
    <span class='thumb-label'>
    <p>pollutionroseplot</p>
    </span>
    </a>
    </div>



.. raw:: html

    <div class='thumb align-center'>
    <a href=./regression.html>
    <img src=../_static/regression_thumb.png>
    <span class='thumb-label'>
    <p>regplot</p>
    </span>
    </a>
    </div>





.. raw:: html

    <div style="clear: both"></div>
