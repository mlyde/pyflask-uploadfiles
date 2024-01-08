import os
import re
import math
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash

app = Flask(__name__)
# 定义上传文件夹的路径
app.config['UPLOAD_FOLDER'] = 'floder/'
# 允许上传文件的种类
# app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'jpg', 'jpeg', 'zip', '7z'])
# 上传文件的最大大小(字节),过大会 RequestEntityTooLarge
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * (1024*1024)	# 1 G
# 密钥用于Session,Cookies...
# app.config['SECRET_KEY'] = "something"

@app.route("/")
def webpage_root():
	return index()

@app.route("/index.html")
def index():
	try:
		return send_from_directory('./', 'index.html')
	except Exception as e:
		return str(e)
	# with open('./index.html', 'r', encoding='utf-8') as f:
	# 	return f.read()

@app.route("/simple.html")
def simple():
	try:
		return send_from_directory('./', 'simple.html')
	except Exception as e:
		return str(e)

@app.route("/images/<filename>", methods=['GET'])
def favicon(filename):
	try:
		return send_from_directory('./images/', filename)
	except Exception as e:
		return str(e)

@app.route("/js/<filename>", methods=['GET'])
def jsFile(filename):
	try:
		return send_from_directory('./js/', filename)
	except Exception as e:
		return str(e)

@app.route('/uploader',methods=['GET','POST'])
def uploader():
	if request.method == 'POST':
		# 检查 post 中有无文件
		if "file" not in request.files:
			print('No file part')
			return redirect(request.url)

		upload_files = request.files.getlist("file")
		# file = request.files['file']	# 获取单个文件

		# 若为空文件
		if upload_files[-1].filename == '':
			# flash('No selected file')
			return redirect(request.url)

		for file in upload_files:
			print(file.filename)
			if('/' in file.filename):
				dir = app.config['UPLOAD_FOLDER'] + file.filename.rsplit('/', 1)[0]
				filename = re.sub(r"[:*?\"<>|]", '-', file.filename.rsplit('/', 1)[-1])
				# 创建文件夹路径
				if not os.path.exists(dir):
					os.mkdir(dir)
			else:
				dir = app.config['UPLOAD_FOLDER']
				filename = re.sub(r"[:*?\"<>|]", '-', file.filename)

			file.save(os.path.join(dir, filename))
			# 使用安全文件名(只支持英文)
			# from werkzeug.utils import secure_filename
			# file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))

		return 'file uploaded successfully'
	else:
		return redirect(url_for("index"))

@app.route("/download/", methods=["GET"], strict_slashes=False, endpoint="download")
@app.route("/download/<path:filename>", methods=["GET"], strict_slashes=False, endpoint="download")
def showFolder(filename = None):
	def randSize(value):
		if value == 0:
			return "0 B"
		unit = ["B","KB","MB","GB","TB","PB","EB","ZB","YB"]
		index = int(math.log(value, 1024))
		size = value/math.pow(1024, index)
		return str(float("%.2f" % size)) + ' ' + unit[index]

	def getFloderFile(dir):
		files_list = os.listdir(dir)
		files_list.sort(key=lambda a: a.lower())
		for i, item in enumerate(files_list):
			size = ''
			print(dir + item)
			fdir = dir + item
			if os.path.isfile(fdir):
				size = randSize(os.path.getsize(fdir))
			files_list[i] = [fdir.split('/',1)[-1], item, size]
		return files_list

	if filename:
		# /download/...
		if filename[-1] == '/':
			# /download/folder.../
			dir = app.config["UPLOAD_FOLDER"] + '/' + filename
			if not os.path.isfile(dir):
				return render_template("manage.html", files_list=getFloderFile(dir))
		else:
			l = filename.rsplit('/', 1)
			if len(l) == 2:
				# /download/name 
				[folder, name] = l
				return send_from_directory(app.config["UPLOAD_FOLDER"] + '/' + folder, name)
			else:
				# /download/folder.../name
				name = l[-1]
				return send_from_directory(app.config["UPLOAD_FOLDER"], name)
	else:
		# /download/
		return render_template("manage.html", files_list=getFloderFile(app.config['UPLOAD_FOLDER']))

# 自定义404界面
# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('page_not_found.html'), 404

if __name__ == '__main__':
	print("cwd:", os.getcwd())
	# app.run(host='0.0.0.0', port=80, debug=True)
	app.run(host='0.0.0.0', port=80, debug=False)
