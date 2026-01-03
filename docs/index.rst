Online Retail Simulator Documentation
=====================================

Generate synthetic retail data for testing, demos, and experimentation without exposing real business data.

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Overview
--------

The Online Retail Simulator is a lightweight Python package for generating synthetic retail data for experimentation and causal inference in e-commerce contexts. It provides realistic product catalogs and daily sales transactions with configurable parameters and reproducible results.

Key Features
~~~~~~~~~~~~

* **Two simulation modes**: Rule-based (simple) and synthesizer-based (ML-powered with SDV)
* **Configuration-driven workflow** for easy customization
* **Deterministic output** with seed control for reproducibility
* **Realistic data patterns** across 8 product categories
* **Treatment effect simulation** for A/B testing scenarios
* **Pandas integration** with native DataFrame output

Quick Start
-----------

.. code-block:: bash

   # Install
   pip install -e .

   # Run demo
   python demo/run_all_demos.py

For detailed installation instructions, tutorials, and use cases, see the :doc:`user-guide`.

Documentation Structure
-----------------------

This documentation is organized into:

* **User Guide**: Tutorials, use cases, and practical examples for all skill levels
* **Configuration Reference**: Complete parameter documentation
* **API Reference**: Detailed function and class documentation
* **Design Architecture**: System design and extension points

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   notebooks/package_overview
   user-guide
   configuration
   design
   api_reference

Getting Help
------------

* **GitHub Issues**: Report bugs or request features
* **User Guide**: Start with tutorials and examples
* **Configuration Reference**: Complete parameter documentation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
