#ifndef _VIDEO_CAPTURE_H_
#define _VIDEO_CAPTURE_H_

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*NOTIFY_ITEM_CALLBACK)(int sku_id, int num);
typedef void (*TOGGLE_CAPTURE_CALLBACK)(unsigned int is_capturing);

int run(NOTIFY_ITEM_CALLBACK cb);
void stop();
void toggle_capture(unsigned int is_capturing, TOGGLE_CAPTURE_CALLBACK cb);

#ifdef __cplusplus
}
#endif

#endif
