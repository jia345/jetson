#ifndef _VIDEO_CAPTURE_H_
#define _VIDEO_CAPTURE_H_

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*NOTIFY_ITEM_CALLBACK_C)(int sku_id, int num);
typedef void (*TOGGLE_CAPTURE_CALLBACK_C)(unsigned int is_capturing);

int run_c(NOTIFY_ITEM_CALLBACK_C cb);
void stop_c();
void toggle_capture_c(unsigned int is_capturing, TOGGLE_CAPTURE_CALLBACK_C cb);

#ifdef __cplusplus
}
#endif

#endif
