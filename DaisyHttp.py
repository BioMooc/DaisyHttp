# Four aims:
# 1. CORS #ok
# 2. range header #ok
# 3. can return file list #ok
# 4. can set root path #ok


# history logs:
#v0.1 init;
#v0.2 ok now;
#v0.3 sopport port;
#v0.4 setting rootPath from cmd;
#v0.5 combine the two cmd(/list, /file) to one, when the path is a file, /list/ is the same as /file/

version="v0.5"

# how to run v0.5:
#$ python3 DaisyHttp.py 8001 /home/wangjl/
# there are two cmd in the URL: /list/ and /file/


"""
test CORS 
$ python3 f5.py 8001 /home/wangjl/data/web/docs
http://ielts.biomooc.com/listening/player.html?url=http://192.168.2.120:8001/file/audio/20041118_day_10-Atlantis.mp3

服务器支持 range, 就可以断点续传
$ curl -H "Range: bytes=10-100" http://192.168.2.120:8001/file/audio/log.txt
$ curl -H "Range: bytes=100-200" http://192.168.2.120:8001/file/audio/log.txt
"""



import os
import re
import json
import mimetypes
from flask import Flask, escape, request, send_file,Response,make_response
app = Flask(__name__)

#####################
# settings
#####################
# aim4. set root path; use absolute path from pwd;
# rootPath="../"
#rootPath="/home/wangjl/"

# add port 
# refer https://github.com/danvk/RangeHTTPServer/blob/master/RangeHTTPServer/__main__.py
import argparse
parser = argparse.ArgumentParser(description= f'DaisyHttp (version {version}) \
    can be used as Data Center Server for Bio Big Files (bam, fasta, ...), with CORS and range header enabled.')
parser.add_argument('port', action='store',
                    default=8000, type=int,
                    nargs='?', help='Specify alternate port [default: 8000]')
parser.add_argument('rootPath', action='store',
                    default=os.getcwd(), type=str,
                    nargs='?', help='Specify the root path [default: /home/]')
args = parser.parse_args()
rootPath = args.rootPath;
print(">> port:", args.port)
print(">> rootPath:", rootPath)




#####################
# help page.
#####################
# help info
@app.route('/')
def hello():
    # name = request.args.get("name", "World")
    # return f'Hello, {escape(name)}!'
    
    help= "<div style='width:800px; margin:10px auto;'>"+\
    f'<h1>DaisyHttp version {version}</h1>' +\
    '1. start this server <b>$ python3 DaisyHttp.py 8001 /home/wangjl/data/web/docs</b>' +\
    f'<br><b>--help</b>: ' +\
    f'<br><b>--port</b>: {escape(args.port)} # this can be set from command line' +\
    f'<br><b>--rootPath</b>: {escape(rootPath)} # this can be set from command line'
    message="""
    <br><br>2. <a href='/list/'>/list/</a> files under this dir: <b>/list/</b>you/dir/path/, don't use . or ..
    <br>    Notice: the dir is based on your rootPath you set before.
<pre>
    eg: If you want to list dir /, browser http://IP:port/list/
    eg: If you want to list dir /data/web/docs/audio/, brower http://IP:port/list/data/web/docs/audio/
    when you put a file after /list/, then it is the same as /file/, 
    and you'll also get the file with CORS and range enabled.</pre>

    <br><br>3. Get the file: <b>/file/</b>you/file/path/.
<pre>
    eg: http://IP:port/file/data/web/docs/audio/20041118_day_10-Atlantis.mp3
</pre>
    </div>
    """
    
    return help+message;




#####################
# /file/
#####################
# aim2. return a file, support range header
# https://programtalk.com/python-examples/flask.request.headers.get/?ipage=2
# https://programtalk.com/vs4/python/2323/scout/scout/blueprints/pileup/partial.py/

BYTE_RANGE_RE = re.compile(r'bytes=(\d+)-(\d+)?$')
def parse_byte_range(byte_range):
    '''Returns the two numbers in 'bytes=123-456' or throws ValueError.
    The last number or both numbers may be None.
    '''
    if byte_range.strip() == '':
        return None, None

    m = BYTE_RANGE_RE.match(byte_range)
    if not m:
        raise ValueError('Invalid byte range %s' % byte_range)

    first, last = [x and int(x) for x in m.groups()]
    if last and last < first:
        raise ValueError('Invalid byte range %s' % byte_range)
    return first, last


# get the file, support CORS and range header;
@app.route('/file/<path:path>')
#def downloader(filename):
#    return send_from_directory("data",filename,as_attachment=False)
def send_file_partial(path):
    pathT = os.path.join(rootPath, path) #真实路径
    print("rootPath:", rootPath)
    
    range_header = request.headers.get('Range', None)
    # aim1: CORS
    if not range_header:
        response = make_response(send_file( pathT, as_attachment=False))
        response.headers["Access-Control-Allow-Origin"]="*"
        return response

    try:
        byte_range = parse_byte_range(request.headers['Range'])
    except ValueError as error:
        return abort(400, 'Invalid byte range')
    first, last = byte_range

    try:
        data = None
        with open(pathT, 'rb') as file_handle:
            fs = os.fstat(file_handle.fileno())
            file_len = fs[6]
            if first >= file_len:
                return abort(416, 'Requested Range Not Satisfiable')

            if last is None or last >= file_len:
                last = file_len - 1
            response_length = last - first + 1

            file_handle.seek(first)
            data = file_handle.read(response_length)
    except IOError:
        return abort(404, 'File not found')

    resp = Response(data, 206, mimetype=mimetypes.guess_type(pathT)[0],
                    direct_passthrough=True)

    resp.headers.add('Content-type', 'application/octet-stream')
    resp.headers.add('Accept-Ranges', 'bytes')
    resp.headers.add('Content-Range',
                     'bytes %s-%s/%s' % (first, last, file_len))
    resp.headers.add('Content-Length', str(response_length))
    # aim1: CORS
    resp.headers["Access-Control-Allow-Origin"]="*"
    return resp




#####################
# /list/
#####################
# aim3: list the files under a dir, mark files and dirs
@app.route('/list/')
def show_subpath0():
    return show_subpath("./")

@app.route('/list/<path:subpath>')
def show_subpath(subpath):
    subpathT = os.path.join(rootPath, subpath) #真实路径
    #import glob
    #arr=glob.glob( subpath + "/*")
    arrF=[]
    arrD=[]
    # 如果是文件夹，则列出内容
    if os.path.isdir(subpathT):
        arr = os.listdir(subpathT)
        for i in arr:
            if os.path.isfile(subpathT+i):
                arrF.append(i)
            else:
                arrD.append(i)
    
        arr={
            "current_dir": subpath,
            "files": arrF,
            "directories": arrD
        }
        # show the subpath after /list/
        return json.dumps(arr)
    else:
        #如果是文件，则显示文件
        return send_file_partial(subpath)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=args.port, debug=True)