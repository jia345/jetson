%module(director="1") video_capture
%{

#include "video_capture.h"

static PyObject *cb_notify_item_py = NULL;
static PyObject *cb_toggle_capturing_py = NULL;

static void _cb_notify_item(int sku_id, int num)
{
   PyObject *func, *arglist;
   PyObject *result;

   func = cb_notify_item_py;     /* This is the function .... */
   arglist = Py_BuildValue("()");  /* No arguments needed */
   result =  PyEval_CallObject(func, arglist);
   Py_DECREF(arglist);
   Py_XDECREF(result);
   return /*void*/;
}

void run(PyObject *PyFunc)
{
    Py_XDECREF(cb_notify_item_py);          /* Dispose of previous callback */
    Py_XINCREF(PyFunc);         /* Add a reference to new callback */
    cb_notify_item_py = PyFunc;         /* Remember new callback */
    run_c(_cb_notify_item);
}

%}

//typedef void (*NOTIFY_ITEM_CALLBACK)(int sku_id, int num);
//typedef void (*TOGGLE_CAPTURE_CALLBACK)(unsigned int is_capturing);
//
//int run(NOTIFY_ITEM_CALLBACK cb);
//void stop();
//void toggle_capture(unsigned int is_capturing, TOGGLE_CAPTURE_CALLBACK cb);

%{
typedef void (*CALLBACK)(void);
extern CALLBACK my_callback;

extern void set_callback(CALLBACK c);
extern void my_set_callback(PyObject *PyFunc);

extern void test(void);
%}

extern CALLBACK my_callback;

extern void set_callback(CALLBACK c);
extern void my_set_callback(PyObject *PyFunc);

extern void test(void);

%{
static PyObject *my_pycallback = NULL;
static void PythonCallBack(void)
{
   PyObject *func, *arglist;
   PyObject *result;

   func = my_pycallback;     /* This is the function .... */
   arglist = Py_BuildValue("()");  /* No arguments needed */
   result =  PyEval_CallObject(func, arglist);
   Py_DECREF(arglist);
   Py_XDECREF(result);
   return /*void*/;
}

void my_set_callback(PyObject *PyFunc)
{
    Py_XDECREF(my_pycallback);          /* Dispose of previous callback */
    Py_XINCREF(PyFunc);         /* Add a reference to new callback */
    my_pycallback = PyFunc;         /* Remember new callback */
    set_callback(PythonCallBack);
}

%}

%typemap(python, in) PyObject *PyFunc {
  if (!PyCallable_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Need a callable object!");
      return NULL;
  }
  $1 = $input;
}