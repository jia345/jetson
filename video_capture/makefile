CC=gcc
DEPS=video_capture.h
OBJS=video_capture.o video_capture_wrap.o

CFLAGS =-O2
CFLAGS+=-fPIC
CFLAGS+=-I.
CFLAGS+=-I/usr/include/python2.7

LDFLAGS=-shared

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

#video_capture_wrap.c: video_capture.i video_capture.h
#	swig -python video_capture.i

all: $(OBJS)
	$(CC) -o _video_capture.so -shared $(OBJS)

clean:
	@rm -f *.o *.so *.pyc *.py video_capture_wrap.c
