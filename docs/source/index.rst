
.. pynamo documentation master file, created by
   sphinx-quickstart on Mon Mar  3 06:40:51 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pynamo
======

A lightweight, client-agnostic Python ORM for Amazon DynamoDB.


Features
========

* Pure ORM layer - Does not concern with connection management
* Fully client-agnostic - no hard dependency on boto3 or AWS SDKs
* Supports single table patterns
* Can be used in either sync or async applications
* Easily create custom fields
* Session management to track changes


.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   usage



.. toctree::
   :maxdepth: 2
   :caption: User's Guide

   tables
   attribute
   models
