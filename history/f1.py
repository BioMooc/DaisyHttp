# 4 task:
# - CORS
# - range header
# - can return file list
# - can set root path


from flask import Flask, escape, request, send_file

app = Flask(__name__)


@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'


# return this file, use range header
@app.route('/path/<path:path>')
#def downloader(filename):
#    return send_from_directory("data",filename,as_attachment=False)
def send_file_partial(path):
    range_header = request.headers.get('Range', None)
    if not range_header:
        return send_file(path)

    try:
        byte_range = parse_byte_range(request.headers['Range'])
    except ValueError as error:
        return abort(400, 'Invalid byte range')
    first, last = byte_range

    try:
        data = None
        with open(path, 'rb') as file_handle:
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

    resp = Response(data, 206, mimetype=mimetypes.guess_type(path)[0],
                    direct_passthrough=True)

    resp.headers.add('Content-type', 'application/octet-stream')
    resp.headers.add('Accept-Ranges', 'bytes')
    resp.headers.add('Content-Range',
                     'bytes %s-%s/%s' % (first, last, file_len))
    resp.headers.add('Content-Length', str(response_length))
    return resp




# list the files under this dir
@app.route('/show/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return 'Subpath %s' % escape(subpath)



if __name__ == '__main__':
    ####默认监听127.0.0.1:5000   关闭调试模式
    app.run(host='0.0.0.0',port=8001,debug=True)