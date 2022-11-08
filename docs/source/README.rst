Moildev_Utils Documentation
======================

Moildev_utils is high level Application Programming Interface (API) that provide the function to process fisheye image for generate Anypoint view, Panorama view and Reverse image view.
This function originally was written on C++ to take the advantage of speed computation.  We know that C++ is static programming language that hard to maintain, be a reason we provide Moildev for python. We use pybind11 for bridge between C++ and python, the architecture of the SDK can be seen on figure bellow this.

.. image:: assets/17.png
   :scale: 90 %
   :alt: alternate text
   :align: center
|

The class of Moutils
The name class is Moutils Its required parameter camera parameter which is .json file from camera calibration in MOIL Lab.

