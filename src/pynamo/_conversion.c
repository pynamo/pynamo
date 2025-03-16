#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *convert_number(PyObject *self, PyObject *args)
{
    const char *value;
    char *end;
    long result;

    if (!PyArg_ParseTuple(args, "s", &value))
    {
        return NULL;
    }

    result = strtol(value, &end, 10);

    if (*end != '\0')
    {
        PyErr_SetString(PyExc_ValueError, "Invalid integer format");
        return NULL;
    }

    return PyLong_FromLong(result);
}

static PyMethodDef ConversionMethods[] = {
    {"convert_number", convert_number, METH_VARARGS, "Convert string to integer"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef conversionmodule = {
    PyModuleDef_HEAD_INIT,
    "pynamo._conversion", // Module name
    NULL,
    -1,
    ConversionMethods};

PyMODINIT_FUNC PyInit__conversion(void)
{
    return PyModule_Create(&conversionmodule);
}
