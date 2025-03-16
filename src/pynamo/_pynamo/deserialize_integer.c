#include "pynamo.h"
#include <stdlib.h>

PyObject *deserialize_integer(PyObject *self, PyObject *args)
{
    PyObject *value;

    if (!PyArg_ParseTuple(args, "O", &value))
    {
        return NULL;
    }

    // Handle None
    if (value == Py_None)
    {
        Py_RETURN_NONE;
    }

    // Handle integer
    if (PyLong_Check(value))
    {
        Py_INCREF(value);
        return value;
    }

    // Handle boolean
    if (PyBool_Check(value))
    {
        return PyLong_FromLong(value == Py_True ? 1 : 0);
    }

    // Handle float
    if (PyFloat_Check(value))
    {
        double float_val = PyFloat_AsDouble(value);
        long int_val = (long)float_val;
        return PyLong_FromLong(int_val);
    }

    // Handle string conversion
    if (PyUnicode_Check(value))
    {
        const char *str = PyUnicode_AsUTF8(value);
        if (str == NULL)
        {
            return NULL; // Conversion failed
        }

        char *end;
        long result = strtol(str, &end, 10);
        if (*end != '\0')
        {
            PyErr_SetString(PyExc_ValueError, "Invalid integer value");
            return NULL;
        }
        return PyLong_FromLong(result);
    }

    // Unsupported type
    PyErr_SetString(PyExc_TypeError, "Unsupported type for integer conversion");
    return NULL;
}
