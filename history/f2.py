# Four aims:
# 1. CORS #ok
# 2. range header #ok
# 3. can return file list #ok
# 4. can set root path #ok

#v0.1 init;
#v0.2 ok now;


import os
import re
import mimetypes
from flask import Flask, escape, request, send_file,Response,make_response
app = Flask(__name__)

#####################
# settings
#####################
# aim4. set root path; use absolute path from pwd;
# rootPath="../"
rootPath="/home/wangjl/"




#####################
# working area.
#####################
# help info
@app.route('/')
def hello():
    # name = request.args.get("name", "World")
    # return f'Hello, {escape(name)}!'
    
    help= 'Help page of this data center.<hr>' +\
    f'1. <b>rootPath</b>: {escape(rootPath)}'
    message="""
    <br><br>2. <a href='/list/'>/list/</a> files under this dir: <b>/list/</b> put your path here, don't use . or ..
    <br>    notice: the dir is based on your rootPath you set in 1(in Settings of this script).
    <br>    eg: list dir / http://IP:port/list/
    <br>    eg: list dir /data/web/docs/audio/ http://IP:port/list/data/web/docs/audio/

    <br><br>3. Get the file: <b>/file/</b> put the path of your file here.
    <br>    eg: http://IP:port/file/data/web/docs/audio/20041118_day_10-Atlantis.mp3
    """
    
    return help+message;





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
    return first, last #可以返回多个值，其实就是 (1,2,3, ...)


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
    resp.headers.add('Content-Range', 'bytes %s-%s/%s' % (first, last, file_len))
    resp.headers.add('Content-Length', str(response_length))
    # aim1: CORS
    resp.headers["Access-Control-Allow-Origin"]="*"
    return resp





# aim3: list the files under a dir, mark files and dirs
@app.route('/list/')
def show_subpath0():
    return show_subpath("./")

@app.route('/list/<path:subpath>')
def show_subpath(subpath):
    subpathT = os.path.join(rootPath, subpath) #真实路径
    #import glob
    #arr=glob.glob( subpath + "/*")
    arr = os.listdir(subpathT)
    arrF=[]
    arrD=[]
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
    
    import json
    # show the subpath after /path/
    return json.dumps(arr)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8001,debug=True)