import os
import urllib2
import math

def downloadChunks(url):
    """Helper to download large files
    the only arg is a url
    this file will go to a temp directory
    the file will also be downloaded
    in chunks and print out how much remains
    """
    baseFile = os.path.basename(url)

    #move the file to a more uniq path
    os.umask(0002)
    temp_path = "/tmp/"
    try:
        file = os.path.join(temp_path,baseFile)
        req = urllib2.urlopen(url)
        total_size = int(req.info().getheader('Content-Length').strip())
        downloaded = 0
        CHUNK = 256 * 10240
        print "download "+file 
        with open(file, 'wb') as fp:
            while True:
                chunk = req.read(CHUNK)
                downloaded += len(chunk)
                print math.floor( (downloaded / total_size) * 100 )
                if not chunk: break
                fp.write(chunk)
    except urllib2.HTTPError, e:
        print "HTTP Error:",e.code , url
        return "" 
    except urllib2.URLError, e:
        print "URL Error:",e.reason , url
        return "" 

    return file

def main():
    downloadChunks("http://135.251.101.152:80/test.bin.gz")  

if __name__ == "__main__":
    main()
