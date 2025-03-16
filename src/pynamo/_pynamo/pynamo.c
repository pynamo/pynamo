#include "pynamo.h"
// Method table
static PyMethodDef PynamoMethods[] = {
    {"deserialize_integer", deserialize_integer, METH_VARARGS, "Convert value to integer"},
    {NULL, NULL, 0, NULL}};

// Module definition
static struct PyModuleDef pynamomodule = {
    PyModuleDef_HEAD_INIT,
    "pynamo.deserialize_integer",
    NULL,
    -1,
    PynamoMethods};

// Initialize module
PyMODINIT_FUNC PyInit__pynamo(void)
{
    return PyModule_Create(&pynamomodule);
}
