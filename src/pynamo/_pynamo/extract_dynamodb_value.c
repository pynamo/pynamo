#include "pynamo.h"

PyObject *extract_dynamodb_value(PyObject *self, PyObject *args)
{
    PyObject *attr_dict;

    if (!PyArg_ParseTuple(args, "O", &attr_dict))
    {
        return NULL;
    }

    // Not a dict or emtpy dict
    if (!PyDict_Check(attr_dict) || PyDict_Size(attr_dict) == 0)
    {
        Py_RETURN_NONE;
    }

    // If "NULL" key is present
    if (PyDict_GetItemString(attr_dict, "NULL") != NULL)
    {
        Py_RETURN_NONE;
    }

    // Extract
    PyObject *key;
    PyObject *value;
    Py_ssize_t pos = 0;

    if (PyDict_Next(attr_dict, &pos, &key, &value))
    {
        Py_INCREF(value);
        return value;
    }
    Py_RETURN_NONE;
}
