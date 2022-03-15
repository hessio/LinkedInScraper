from flask import Flask, flash, request, redirect, render_template, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from config import *
import os 
import pandas as pd

from about import about_api
from upload import upload_api
from search import search_api
#from read_job_desc import job_desc_api

app=Flask(__name__)
app.secret_key = 'secretKey'

app.register_blueprint(about_api)
app.register_blueprint(upload_api)
app.register_blueprint(search_api)
#app.register_blueprint(job_desc_api)

if not os.path.isdir(upload_dest):
    os.mkdir(upload_dest)

app.config['MAX_CONTENT_LENGTH'] = file_mb_max * 1024 * 1024

@app.context_processor
def handle_context():
    return dict(os=os)

@app.route('/list')
def list():
  	return render_template('list.html', files=upload_dest)

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
	workingdir = os.path.abspath(os.getcwd())
	filepath = workingdir+'/static/files/'
	filename, file_extension = os.path.splitext(filename)
	if file_extension == '.csv':
		with open(filepath+filename) as fp:
			csv = fp.read()
		return Response(
	        csv,
	        mimetype="text/csv",
	        headers={"Content-disposition":
	                 f"attachment; filename={filename+'.'+file_extension}"})
	if file_extension == '.pdf':
		print("YES BOI")
		return Response(filename, 
			mimetype="application/pdf",
			headers={"Content-disposition":
	                 f"attachment; filename={filename+'.'+file_extension}"})
	return 'done'

@app.route('/')
def welcome():
	return render_template('index.html')

@app.route('/open/<upload>')
def open(upload):
	workingdir = os.path.abspath(os.getcwd())
	filepath = workingdir+'/static/files/'
	return send_from_directory(filepath, upload)

@app.route('/display_stats/<upload>')
def display_stats(upload):
	df = pd.read_csv(upload_dest+'/'+upload)
	df['date'] = pd.to_datetime(df['date'])
	df_ = df.groupby([df['date'].dt.date]).mean()
	df_['Standard deviation for age on this date'] = df.groupby([df['date'].dt.date]).std()
	df_ = df_.rename(columns={'age': 'Average age for this date'})
	return render_template('display_stats.html',  stats=[df_.to_html(classes='data', header="true")])

@app.route('/thank_you/<name>')
def thank_you(name):
	render_template('thank_you.html', user=name)

if __name__ == "__main__":
    print('to upload files navigate to http://127.0.0.1:4000/search')
    app.run(host='127.0.0.1',port=4000,debug=True,threaded=True)