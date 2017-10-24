# -*- coding: utf-8 -*-

from twisted.internet import reactor, threads
import time
import download_from_url
import json
import os
from os.path import expanduser

class swUpdate():
    def __init__(self,cb_download=None, cb_update=None):
        self.sw_update_cb = cb_update; 
        self.sw_download_cb = cb_download;
        self.downloaded_files=["","",""];
        self.downloaded=False;
        self.downloading=False;
        self.can_update=False;
    
    
    def append_current_ver(self, post_data):
        home = expanduser("~")
        main_fn=home+"/main.ver"
        main_f = open(main_fn)
        try:
            main_ver=main_f.readline()
            main_ver=main_ver.strip('\n');
        finally:
            main_f.close()

        model_fn=home+"/model.ver"
        model_f = open(model_fn)
        try:
            model_ver=model_f.readline()
            model_ver=model_ver.strip("\n");
        finally:
            model_f.close()
        web_fn=home+"/web.ver"
        web_f = open(web_fn)
        try:
            web_ver=web_f.readline()
            web_ver=web_ver.strip("\n")
        finally:
            web_f.close()
        current_ver={'ver':{'main':main_ver,'model':model_ver,'web':web_ver}}
        return dict(post_data.items()+current_ver.items())

    def can_send_readyupdate(self):
        if self.downloaded==True:
            return True
        return False

    def has_download_urls(self, urls):
        get_json = json.loads(urls)
        xx = get_json['ver'] if 'ver' in get_json else ""
        if xx == "":
            return False
        x = get_json['ver']['main'] if 'main' in get_json['ver'] else ""
        if  x != "" :
            return True
        x = get_json['ver']['model'] if 'model' in get_json['ver'] else ""
        if  x != "" :
            return True
        x = get_json['ver']['web'] if 'web' in get_json['ver'] else ""
        if  x != "" : 
            return True;
        return False

    def download_cb(result):
        print "dowload result =", result
    
    def sw_download(self, urls):
        if self.has_download_urls(urls) == True and self.downloading==False:
            self.downloading=True
            get_json = json.loads(urls)
            xx = get_json['ver'] if 'ver' in get_json else ""
            if xx == "":
                return

            call_cb = False 
            x = get_json['ver']['main'] if 'main' in get_json['ver'] else ""
            if  x != "" :
                self.downloaded_files[0]=download_from_url.downloadChunks(x)
                call_cb=True
            else:
                self.downloaded_files[0]=""

            x = get_json['ver']['model'] if 'model' in get_json['ver'] else ""
            if  x != "" :
                self.downloaded_files[1]=download_from_url.downloadChunks(x)
                call_cb=True
            else:
                self.downloaded_files[1]=""

            x = get_json['ver']['web'] if 'web' in get_json['ver'] else ""
            if  x != "" : 
                self.downloaded_files[2]=download_from_url.downloadChunks(x)
                call_cb=True
            else:
                self.downloaded_files[2]=""
            
            print self.downloaded_files
            if self.sw_download_cb!= None and call_cb==True:
                self.sw_download_cb()
            self.downloaded=True

    def sw_update(self, resp):
        if self.can_update == True:
            return
        get_json = json.loads(resp)
        print get_json
        xx = get_json['ret'] if 'ret' in get_json else ""
        if xx == "":
            self.can_update=False
            return

        x = get_json['ret']['action'] if 'action' in get_json['ret'] else ""
        if  x == "" :
            self.can_update=False
            return
        if x == "upgrade":
            self.can_update=True
       
        while self.downloaded==False:
            sleep(1)  
        file_num = len(self.downloaded_files)
        for f in self.downloaded_files :
            if f != "" :
                print "update file "+f;
                cmd = "cd /tmp && tar xvfz " +f
                print cmd
                os.system(cmd)

        if self.sw_update_cb!= None and file_num>0:
            self.sw_update_cb()

if __name__ == "__main__":
    a_swUpdate = swUpdate()
    urls='{"ver":{"web":"http://135.251.101.152:80/html.gz"}}'
    #reactor.callInThread(a_swUpdate.sw_download,urls)
    #print  "after def download"
    #a_swUpdate.sw_update()
    post_data={}
    print a_swUpdate.append_current_ver(post_data)
    a_swUpdate.sw_download(urls)
    reactor.run()
