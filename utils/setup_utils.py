import logging
import argparse
import yaml
import urllib
from datetime import datetime
import sys
import os

from objects.hub import Hub
from objects.image import App

#prints a progress bar as a process runs with
#how many items are complete, how many need to complete,
#and the length of the bar on the screen
def progress_bar(num, total, length):
	#get decimal and integer percent done
	proportion = num / total
	percent = int(proportion * 100)
	#get number of octothorpes to display
	size = int(proportion * length)
	#display [###   ] NN% done
	display = '[' + ('#' * size) + (' ' * (length - size)) + '] ' + str(percent) + '% done'
	#write with stdout to allow for in-place printing
	sys.stdout.write(display)
	sys.stdout.flush()
	sys.stdout.write("\b" * 300)
	#return the proportion for logging
	return percent

def setup_logging():
	"""Begin execution here.
	Before we call main(), setup the logging from command line args """
	parser = argparse.ArgumentParser(
					description="A script to get information about images from DockerHub")

	parser.add_argument("user", type=argparse.FileType('r'), help="user.yaml contains creds for Dockerhub and Github")
	parser.add_argument("-d", "--debug",
						help="DEBUG output enabled. Logs a lot of stuff",
						action="store_const", dest="loglevel",
						const=logging.DEBUG, default=logging.WARNING)

	parser.add_argument("-v", "--verbose", help="INFO logging enabled",
					action="store_const", dest="loglevel", const=logging.INFO)

	parser.add_argument("-i", "--index", help="A index.yaml file from a Helm Chart", type=argparse.FileType('r'))

	parser.add_argument("-k", "--keep", help="Keeps old values and chart files", action="store_true", dest="keep_files")
		
	args = parser.parse_args()
		
	logging.getLogger("requests").setLevel(logging.WARNING) #turn off requests

	# let argparse do the work for us
	logging.basicConfig(level=args.loglevel,filename='container-output.log',
						format='%(levelname)s:%(message)s')

	return args

def parse_creds(creds_file_loc):
	hub_list = []
	github_token = ""

	with open(creds_file_loc, 'r') as creds_file:	#Open up creds_file (typically user.yaml) 
		raw_yaml_input = yaml.safe_load(creds_file)	#load the yaml from creds file
		for site_info in raw_yaml_input['registries'].items():	#for each site with creds
			if "hub.docker.com" in site_info[0]:		#site_info[0] is url of site
				"""create a Hub object containing url and creds. return a list of objects"""
				for repos in site_info[1].items():	#site_info[1] is dict of (typically) user:pass
					hub = Hub(site_info[0],repos[0],repos[1]) #Hub(url, user, pass)
					hub_list.append(hub)
			if "github.com" in site_info[0]:
				for tokens in site_info[1].items():
					github_token = tokens[1]

	return hub_list, github_token

def get_index_yaml(args):
	#optional arg for index.yaml from Helm chart, or just download latest from IBM/charts
	if args.index:
		if args.index.name == "index.yaml":
			return str(os.getcwd() + "/" + args.index.name)
		else:
			print("Please only supply a index.yaml from a Helm Chart. \n Exiting.")
			sys.exit()
	else:
		url = "https://raw.githubusercontent.com/IBM/charts/master/repo/stable/index.yaml"
		return urllib.request.urlretrieve(url)[0]	#gets index.yaml and returns localFileName

def parse_index_yaml(index_file_loc):
	app_list = []
	need_keywords_list = []

	with open(index_file_loc, 'r') as index_file:		#open the index file
		index_yaml_doc = yaml.safe_load(index_file)	#and load the yaml to the program

	#keys = MainImage.name, values=other info about the app
	for k, v in index_yaml_doc["entries"].items():	
		app_name = k.replace('/', '')
		url_for_app = "https://raw.githubusercontent.com/IBM/charts/master/stable/{}/".format(app_name)

		try:
			keywords = v[0]['keywords']
		except:
			need_keywords_list.append(app_name)

		main_image = App(app_name, url_for_app)
		for key in keywords:
			main_image.add_keyword(key)
		app_list.append(main_image)
	
	return app_list, need_keywords_list #currently just apps with names and base urls

def setup_output_file():
	""" Initialize the Image object and add tags, repos, and archs to image obj.
	Once Image obj is setup, add it to a sublist of App obj. This function will 
	call output_CSV() for each App from the helm chart."""
	
	#set up file name, make directory if it doesn't exist
	date = datetime.today().strftime("%d-%b-%Y")	#16-Jul-2019
	results_file_loc = "archives/results-{}.csv".format(date)
	os.makedirs("archives", exist_ok=True)

	#re-writes files on the same day, leaves old files
	f = open(results_file_loc, "w+")
	f.write("Product,App,amd64,ppc64le,s390x,Images,Container,amd64,ppc64le,s390x,Tag Exists?\n")
	
	return f
