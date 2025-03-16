#include "pynamo.h"
// Method table
static PyMethodDef PynamoMethods[] = {
    {"deserialize_integer", deserialize_integer, METH_VARARGS, "Deserialize value to integer"},
    {"deserialize_decimal", deserialize_decimal, METH_VARARGS, "Deserialize value to decimal"},
    {"extract_dynamodb_value", extract_dynamodb_value, METH_VARARGS, "Extract DynamoDB value"},
    {NULL, NULL, 0, NULL}};

// Module definition
static struct PyModuleDef pynamomodule = {
    PyModuleDef_HEAD_INIT,
    "_pynamo",
    NULL,
    -1,
    PynamoMethods};

// Initialize module
PyMODINIT_FUNC PyInit__pynamo(void)
{
    init_decimal();
    return PyModule_Create(&pynamomodule);
}
