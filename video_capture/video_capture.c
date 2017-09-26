#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include "video_capture.h"

#define TRUE 1
#define FALSE 0

struct callback_struct {
    NOTIFY_ITEM_CALLBACK cb_notify_item;
    TOGGLE_CAPTURE_CALLBACK cb_toggle_capture;
};

static unsigned int is_capturing = FALSE;
static unsigned int is_running = TRUE;

static TOGGLE_CAPTURE_CALLBACK ext_cb_toggle_capture = NULL;

void toggle_capture(unsigned int is_capturing, TOGGLE_CAPTURE_CALLBACK cb)
{
    is_capturing = is_capturing;
    ext_cb_toggle_capture = cb;
}

static void* capture_thread_func(void *args)
{
    struct callback_struct* cbs = (struct callback_struct*)args;
    NOTIFY_ITEM_CALLBACK cb_notify_item = cbs->cb_notify_item;
    TOGGLE_CAPTURE_CALLBACK cb_toggle_capture = cbs->cb_toggle_capture;

    while (is_running)
    {
        if (is_capturing)
        {
            sleep(2);
            cb_notify_item(12345, 1);
        }
        else
        {
            cb_toggle_capture(is_capturing);
        }
    }
    printf("<VIDEO_CAPTURE>: quit the running loop\n");
}

static void cb_toggle_capture(unsigned int is_capturing)
{
    if (ext_cb_toggle_capture != NULL)
    {
        ext_cb_toggle_capture(is_capturing);
    }
}

int run(NOTIFY_ITEM_CALLBACK cb_notify_item)
{
    printf("<VIDEO_CAPTURE>: hello! I'm ready\n");
    struct callback_struct args;
    args.cb_notify_item = cb_notify_item;
    args.cb_toggle_capture = &cb_toggle_capture;

    pthread_t thread_id;

    pthread_attr_t attr;
    pthread_attr_init(&attr);

    struct sched_param schedParam;
    schedParam.sched_priority = 85;
    pthread_attr_setschedparam(&attr, &schedParam);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);

    void* callback[] = { cb_notify_item, &cb_toggle_capture };
    int ret = pthread_create(&thread_id, &attr, &capture_thread_func, (void*)&args);
    if (0 != ret) {
        pthread_attr_destroy(&attr);
        return -1;
    } else {
        pthread_detach(thread_id);
        pthread_attr_destroy(&attr);
        return 0;
    }
}

void stop()
{
    is_running = FALSE;
}
