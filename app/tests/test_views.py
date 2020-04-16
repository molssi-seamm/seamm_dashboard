"""
Tests for the front end
"""

from flask import url_for

import pytest
import requests
import os

import urllib.parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.usefixtures('live_server')
class TestLiveServer:
    """
    This uses selenium and the 'live_server' fixture which comes with pytest-flask.
    """

    @property
    def base_url(self):
        return url_for('main.index', _external=True)

    def test_main_view(self, app, chrome_driver):
        chrome_driver.get(self.base_url)
        ui_view = chrome_driver.find_element_by_id("ui-view")
        displayed_values = ui_view.find_elements_by_class_name("text-value")
        expected_values = "0 2 0 1 0".split()
        displayed_values = [x for x in displayed_values if x != '']

        for i,value in enumerate(displayed_values):
            assert expected_values[i] == value.get_attribute('innerHTML')
            
    def test_jobs_list(self, app, chrome_driver):
        chrome_driver.get(f"{self.base_url}#jobs")
        
        # Get the jobs table. Will want to wait for this to be loaded, of course.
        jobs_table = WebDriverWait(chrome_driver, 20).until(EC.presence_of_element_located((By.ID, "jobs")))
        
        # Check table dimensions.
        table_headings = jobs_table.find_elements_by_tag_name("th")
        table_rows = jobs_table.find_elements_by_tag_name("tr")
        assert len(table_headings) == 5
        assert len(table_rows) == 3

        # Check the response code of the links in the table.
        table_links = jobs_table.find_elements_by_class_name('nav-link')
        for link in table_links:
            # This is just a thing we have to do because of the way 'nav-links' are handled in the app.
            important_url = link.get_attribute('href')[len(self.base_url):]
            actual_url = f'{self.base_url}/#{important_url}'
            response = requests.get(actual_url)
            assert response.status_code == 200
            
        #chrome_driver.get_screenshot_as_file('test_screenshot.png')

    def test_job_report_file_tree(self, app, chrome_driver):

        # Get page with chromedriver.
        chrome_driver.get(f"{self.base_url}#jobs/1")
        
        # Set up samples for comparison.
        dir_path = os.path.dirname(os.path.realpath(__file__))
        test_dir = os.path.realpath(os.path.join(dir_path, "..", "..", "data", "projects", "MyProject", "Job_000001"))
        
        num_files = len(os.listdir(test_dir))
        
        
        file_tree = chrome_driver.find_element_by_id('js-tree')
        js_tree_contents = file_tree.find_elements_by_tag_name('li')
    
        num_files_in_tree = len(js_tree_contents)

        assert num_files_in_tree == num_files+1


    def test_job_report_load_file(self, app, chrome_driver):
        """

        """
        
        # Set up sample file for comparison.
        dir_path = os.path.dirname(os.path.realpath(__file__))
        test_file = os.path.realpath(os.path.join(dir_path, "..", "..", "data", "projects", "MyProject", "Job_000001", "job.out"))
        with open(test_file) as f:
            file_contents = f.read()
            file_contents_split = file_contents.split()
        
        test_file_id = urllib.parse.quote(test_file, safe='')+'_anchor'
        
        chrome_driver.get(f"{self.base_url}#jobs/1")

        # Initially, there should be nothing in the text box.
        initial_displayed_text = chrome_driver.find_element_by_id('file-content').text
        
        # Get a link for a file and click on it.
        job_link = WebDriverWait(chrome_driver, 20).until(EC.presence_of_element_located((By.ID, test_file_id)))
        job_link.click()

        # When clicked, file text should be displayed in the div.
        displayed_text = chrome_driver.find_element_by_id('file-content').text

        displayed_text_list = displayed_text.split()

        # Splitting on whitespace and rejoining let's us compare the file
        # contents without worrying about how whitespace is handled.
        assert initial_displayed_text == ''
        assert ' '.join(displayed_text_list) == ' '.join(file_contents_split)

        
        
