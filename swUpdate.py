# -*- coding: utf-8 -*-

from twisted.internet import reactor
import time
import download_from_url
import json
import os

class swUpdate():
    def __init__(self,cb_download=None, cb_update=None):
        self.sw_update_cb = cb_update; 
        self.sw_download_cb = cb_download;
        self.downloaded_files=["","",""];

    def get_current_ver(self):
        return {'ver_main_control':'1.0','ver_model':'1.0','ver_html':'1.0'}
    
    def has_update(self, urls):
        get_json = json.loads(urls)
        x = get_json[u'url_main_control'] if u'url_main_control' in get_json else ""
        if  x != "" :
            return True
        x = get_json['url_model'] if 'url_model' in get_json else ""
        if  x != "" :
            return True

        x = get_json['url_html'] if 'url_html' in get_json else ""
        if  x != "" : 
            return True;
        return False

    def sw_download(self, urls):
        get_json = json.loads(urls)
        call_cb = False 
        x = get_json[u'url_main_control'] if u'url_main_control' in get_json else ""
        if  x != "" :
          self.downloaded_files[0]=download_from_url.downloadChunks(x)
          call_cb=True
        else:
          self.downloaded_files[0]=""

        x = get_json['url_model'] if 'url_model' in get_json else ""
        if  x != "" :
          self.downloaded_files[1]=download_from_url.downloadChunks(x)
          call_cb=True
        else:
          self.downloaded_files[1]=""

        x = get_json['url_html'] if 'url_html' in get_json else ""
        if  x != "" : 
          self.downloaded_files[2]=download_from_url.downloadChunks(x)
          call_cb=True
        else:
          self.downloaded_files[2]=""

        print self.downloaded_files
        if self.sw_download_cb!= None and call_cb:
            self.sw_download_cb()

    def sw_update(self):
        for f in self.downloaded_files :
            if f != "" :
                print "update file "+f;
                cmd = "cd /tmp && gzip -f -d -q " +f
                print cmd
                os.system(cmd)

        if self.sw_update_cb!= None :
            self.sw_update_cb()

if __name__ == "__main__":
    a_swUpdate = swUpdate()
    urls='{"url_html":"http://135.251.101.152:80/html.gz"}'
    a_swUpdate.sw_download(urls)
    a_swUpdate.sw_update()
    reactor.run()
