#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <pthread.h>
#include <string.h>
#include <stdlib.h>

#define MAX_THREADS 4 // Adjust based on CPU core count

typedef struct
{
    PyObject *input_dict;
    PyObject *result_dict;
    Py_ssize_t start;
    Py_ssize_t end;
} ThreadData;

void *deserialize_worker(void *arg)
{
    ThreadData *data = (ThreadData *)arg;

    PyObject *key, *value;
    Py_ssize_t pos = data->start;

    while (pos < data->end && PyDict_Next(data->input_dict, &pos, &key, &value))
    {
        PyObject *parsed_value = NULL;

        if (PyDict_Contains(value, PyUnicode_FromString("S")))
        {
            parsed_value = PyDict_GetItemString(value, "S");
            Py_INCREF(parsed_value);
        }
        else if (PyDict_Contains(value, PyUnicode_FromString("N")))
        {
            PyObject *num_val = PyDict_GetItemString(value, "N");
            const char *num_str = PyUnicode_AsUTF8(num_val);
            char *end;
            long int_val = strtol(num_str, &end, 10);
            if (*end == '\0')
            {
                parsed_value = PyLong_FromLong(int_val);
            }
            else
            {
                double float_val = strtod(num_str, &end);
                if (*end == '\0')
                {
                    parsed_value = PyFloat_FromDouble(float_val);
                }
            }
        }
        else if (PyDict_Contains(value, PyUnicode_FromString("BOOL")))
        {
            PyObject *bool_val = PyDict_GetItemString(value, "BOOL");
            parsed_value = PyBool_FromLong(PyObject_IsTrue(bool_val));
        }
        else if (PyDict_Contains(value, PyUnicode_FromString("SS")))
        {
            parsed_value = PyDict_GetItemString(value, "SS");
            Py_INCREF(parsed_value);
        }

        if (parsed_value)
        {
            PyDict_SetItem(data->result_dict, key, parsed_value);
            Py_DECREF(parsed_value);
        }
    }

    pthread_exit(NULL);
}

static PyObject *deserialize_parallel(PyObject *self, PyObject *args)
{
    PyObject *input_dict;
    if (!PyArg_ParseTuple(args, "O", &input_dict))
    {
        return NULL;
    }

    if (!PyDict_Check(input_dict))
    {
        PyErr_SetString(PyExc_TypeError, "Expected a dictionary");
        return NULL;
    }

    // Create result dict
    PyObject *result = PyDict_New();
    Py_ssize_t size = PyDict_Size(input_dict);
    Py_ssize_t chunk_size = size / MAX_THREADS;

    pthread_t threads[MAX_THREADS];
    ThreadData thread_data[MAX_THREADS];

    Py_BEGIN_ALLOW_THREADS; // 🚀 Release the GIL

    for (int i = 0; i < MAX_THREADS; i++)
    {
        thread_data[i].input_dict = input_dict;
        thread_data[i].result_dict = result;
        thread_data[i].start = i * chunk_size;
        thread_data[i].end = (i == MAX_THREADS - 1) ? size : (i + 1) * chunk_size;

        pthread_create(&threads[i], NULL, deserialize_worker, &thread_data[i]);
    }

    for (int i = 0; i < MAX_THREADS; i++)
    {
        pthread_join(threads[i], NULL);
    }

    Py_END_ALLOW_THREADS; // 🚀 Reacquire the GIL

    return result;
}
