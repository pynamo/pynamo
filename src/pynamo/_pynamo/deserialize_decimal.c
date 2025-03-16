#include "pynamo.h"
#include <stdlib.h>

static PyObject *decimal_module = NULL;
static PyObject *decimal_class = NULL;

PyObject *deserialize_decimal(PyObject *self, PyObject *args)
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
    // Already a decimal
    if (PyObject_IsInstance(value, decimal_class))
    {
        Py_INCREF(value);
        return value;
    }
    // Handle String
    if (PyUnicode_Check(value))
    {
        const char *str = PyUnicode_AsUTF8(value);
        if (str == NULL)
        {
            return NULL;
        }

        PyObject *decimal_value = PyObject_CallFunction(decimal_class, "s", str);
        if (decimal_value == NULL)
        {
            return NULL;
        }
        return decimal_value;
    }

    // Handle Floats
    if (PyFloat_Check(value))
    {
        double result = PyFloat_AsDouble(value);
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "%.17g", result);

        PyObject *decimal_value = PyObject_CallFunction(decimal_class, "s", buffer);
        if (decimal_value == NULL)
        {
            return NULL;
        }
        return decimal_value;
    }
    // Handle ints

    if (PyLong_Check(value))
    {
        PyObject *decimal_value = PyObject_CallFunction(decimal_class, "O", value);
        if (decimal_value == NULL)
        {
            return NULL;
        }
        return decimal_value;
    }

    // else error
    PyErr_SetString(PyExc_TypeError, "Unsupported type for decimal deserialization");
    return NULL;
}

int init_decimal(void)
{
    PyObject *decimal_module = PyImport_ImportModule("decimal");
    if (decimal_module == NULL)
    {
        return -1;
    }
    decimal_class = PyObject_GetAttrString(decimal_module, "Decimal");
    if (decimal_class == NULL)
    {
        return -1;
    }
    return 0;
}
