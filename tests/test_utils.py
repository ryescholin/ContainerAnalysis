import pytest
from datetime import datetime, timedelta

from utils.crawler import get_repo_pages
from utils.setup_utils import progress_bar, parse_creds, travis_trial
from utils.setup_utils import parse_index_yaml
from utils.teardown_utils import diff_last_files


# test get_repo_pages from crawler
def test_get_repo_pages_10():
        assert(get_repo_pages(10) == 1)

def test_get_repo_pages_100():
        assert(get_repo_pages(100) == 1)

def test_get_repo_pages_101():
        assert(get_repo_pages(101) == 2)

def test_get_repo_pages_999():
        assert(get_repo_pages(999) == 10)

def test_get_repo_pages_1000():
        assert(get_repo_pages(1000) == 10)


# Just a sanity check, if this fails, something is VERY wrong
def test_travis_1():
    assert(travis_trial() is True)

# test progress_bar function from setup_utils
def test_progress_bar_1_100():
	start_time = datetime.now()
	assert(progress_bar(1, 100, start_time) == 1)

def test_progress_bar_1_50():
	start_time = datetime.now()
	assert(progress_bar(1, 50, start_time) == 2)

def test_progress_bar_466_693():
	start_time = datetime.now()
	assert(progress_bar(466, 693, start_time) == 67)

def test_progress_bar_385_745():
	start_time = datetime.now()
	assert(progress_bar(385, 745, start_time) == 51)

# test parse_creds function from setup_utils
def test_parse_creds():
	assert(parse_creds("docs/test_user.yaml")[0].regis=="hub.docker.com")

# test parse_index_yaml from setup_utils
def test_parse_index_yaml():
	app_list, need_keywords_list=parse_index_yaml("docs/test_index.yaml")
	assert(app_list[0].name == "ibm-ace-dashboard-dev")
	assert(need_keywords_list == [])


# test diff_last_files from setup.utils
def test_diff_last_files_no_yesterday():
	assert(diff_last_files() == "Yesterday not found")

def test_diff_last_files_blank_yesterday():
	# Create a blank yesterday results file, just to test
	yesterday = (datetime.today() - timedelta(1)).strftime("%d-%b-%Y")
	yesterday_file_loc = "archives/results-{}.csv".format(yesterday)
	yesterday_file = open(yesterday_file_loc, "w+")
	yesterday_file.close()
	assert(diff_last_files() == "Finished properly")

