#ifndef PYNAMO_H
#define PYNAMO_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *deserialize_integer(PyObject *self, PyObject *args);
PyObject *deserialize_decimal(PyObject *self, PyObject *args);
PyObject *extract_dynamodb_value(PyObject *self, PyObject *args);

#endif
