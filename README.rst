odmadmpy
========

**odmadmpy** is a quick and dirty Python library to write CCSDS Orbit Data Messages (ODM) and Attitude Data Messages (ADM) files.

Installation
============

.. code-block:: shell

    pip install -r requirements.txt

CCSDS ODM and ADM
=================

The current CCSDS blue books for ODM and ADM, respectively 502x0b2c1 and 504x0b1c1, are available in the `docs` folder.

CIC
===

The CIC format (Centre d'Ingénierie Concourante) is an adaptation of the CCSDS format used by CNES. In addition to orbit and attitude data, it allows to exchange mission data such as satellite geometry, thermal data, electrical data, etc.

This format is used in particular by the Timeloop VTS visualization tool developed by Spacebel and CNES.

The reference manual for the CIC format is not distributed publicly but is provided with the VTS software which can be freely downloaded at https://timeloop.fr/vts/. In the VTS root folder, the manual is located at `Docs/Manual/CIC-Exchange-Protocol-V2.0.pdf`.
