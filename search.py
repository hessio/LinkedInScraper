#!/usr/bin/python

import pandas as pd
import re
from collections import defaultdict
from read_job_desc import job_desc
import bs4
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime

from random import randint
import requests
from collections import defaultdict

from forms import SearchBar

from flask import Blueprint, render_template, request, flash, redirect, url_for
from config import *

search_api = Blueprint('search_api', __name__)

def get_links(job_data):
    job_data_flattened = []
    for i in job_data:
        for j in job_data[i]:
            job_data_flattened.append([i, j])
    return job_data_flattened

def str_to_bs4(string):
	html_soup = BeautifulSoup(string, 'html.parser')
	html_tags = html_soup.find_all('li')
	return html_tags

def get_job_data(location):

	# https://www.linkedin.com/jobs/search?keywords=software%20engineer&position=1&pageNum=0
	url = "https://www.linkedin.com/jobs/search?keywords=software%20engineer&location=" + location + "&trk=homepage-jobseeker_jobs-search-bar_search-submit&position=1&pageNum=0"

	html_content = requests.get(url).text
	soup = BeautifulSoup(html_content, "lxml")

	lists = soup.find_all("ul", {"class": "jobs-search__results-list"})
	lists = str(lists[0])
	print("here are the lists", lists)
	regex = r'<li.*?<\/li>'

	job_listings = re.findall(regex, lists, re.DOTALL)
	print("the job postings whattta ja ", job_listings)
	
	tags = []
	for i in job_listings:
	    i.replace("\n", " ")
	    tag = str_to_bs4(i)
	    tags.append(tag)

	job_data = defaultdict(list)
	company_data = defaultdict(list)

	for job in tags:
	    job =job[0]
	    try:
	    	job_titles = job.find('span',{'class': 'screen-reader-text'}).text.strip()
	    except:
	    	job_titles = job.find('h3',{'class': 'base-search-card__title'}).text.strip()
	    try:
	    	job_links = job.find('a',{'class': 'result-card__full-card-link'})["href"]
	    except:
	    	try:
	    		job_links = job.find('a',{'class': 'base-card__full-link'})["href"]
	    	except:
	    		job_links = job.find('a',{'data-tracking-control-name': 'public_jobs_jserp-result_search-card'})["href"]
	    job_data[job_titles].append(job_links)
	    
	    try:
	        company_titles = job.find('a',{'class': 'result-card__subtitle-link job-result-card__subtitle-link'}).text.strip()
	        company_links = job.find('a',{'class': 'result-card__subtitle-link job-result-card__subtitle-link'})["href"]
	    except:
	    	try:
	    		company_titles = job.find('h4',{'class': 'result-card__subtitle job-result-card__subtitle'}).text.strip()
	    		company_links = 'https://www.google.com/search?q=' + company_titles
	    	except:
	    		company_titles = job.find('a',{'class': 'hidden-nested-link'}).text.strip()
	    		company_links = 'https://www.google.com/search?q=' + company_titles
	    
	    company_data[company_titles].append(company_links)

	return [job_data, company_data]


@search_api.route('/search', methods=['GET', 'POST'])
def search():
	search_bar = SearchBar()
	print("fartsstars", request.method)
	if request.method == 'POST':
		if 'job' in request.form:
			job = request.form['job']
			location = request.form['location']

			job_data = get_job_data(location)
			company_data = job_data[1]
			print(company_data)
			job_data = job_data[0]
			return render_template('search.html', jobs=get_links(job_data),company_info=get_links(company_data))
		elif request.form['apply'] == 'Apply':
			job_desc()
	return render_template('search.html', search_bar=search_bar)
