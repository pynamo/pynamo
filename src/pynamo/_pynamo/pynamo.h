#ifndef PYNAMO_H
#define PYNAMO_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *deserialize_integer(PyObject *self, PyObject *args);

#endif
