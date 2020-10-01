"""
Tests for the front end
"""

from flask import url_for

import pytest
import requests
import os
import platform
import sys

import urllib.parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Needed for Python 3.8 since default for OS/X changed to spawn rather than
# fork.
if sys.version_info >= (3, 8) and platform.system() == 'Darwin':
    import multiprocessing
    multiprocessing.set_start_method("fork")


@pytest.mark.usefixtures('live_server')
class TestLiveServer:
    """
    This uses selenium and the 'live_server' fixture which comes with
    pytest-flask.
    """

    @property
    def base_url(self):
        return url_for('main.index', _external=True)

    def log_in(self, chrome_driver):
        """
        Function to log sample user in for testing.
        """
        login_url = F'{self.base_url}auth/login'
        chrome_driver.get(login_url)

        username_field = chrome_driver.find_element_by_id('username')
        username_field.send_keys('sample_user')

        username_field = chrome_driver.find_element_by_id('password')
        username_field.send_keys('sample_password')

        button = chrome_driver.find_element_by_id('submit')
        button.click()

        # For some reason we need to navigate away from the main page
        # before loading the page of interest or we time out
        chrome_driver.get(f"{self.base_url}api/status")
    
    def log_out(self, chrome_driver):
        """
        Function to make sure we are logged out
        """

        logout_url = F'{self.base_url}auth/logout'

        chrome_driver.get(logout_url)

    @pytest.mark.parametrize("logged_in", [True, False])
    def test_main_view(self, app, chrome_driver, logged_in):

        if logged_in:
            self.log_in(chrome_driver)
            # Should have three finished jobs, 1 flowchart, and 1 project when logged in.
            expected_values = "0 3 0 1 1".split() 

        else:
            # Make sure we are logged out
            self.log_out(chrome_driver)
            # Should have one public job and nothing else.
            expected_values = "0 1 0 0 0".split()
        
        chrome_driver.get(self.base_url)
        ui_view = chrome_driver.find_element_by_id("ui-view")
        displayed_values = ui_view.find_elements_by_class_name("text-value")
        
        displayed_values = [x for x in displayed_values if x != '']

        for i, value in enumerate(displayed_values):
            assert expected_values[i] == value.get_attribute('innerHTML')

    @pytest.mark.parametrize("list_type, num_columns, num_rows, logged_in", [
        ("jobs", 7,4 , True),
        ("jobs", 7, 2, False),
        ("flowcharts", 5, 2, True),
        ("flowcharts", 5, 2, False),
        ("projects", 4, 2, True),
        ("projects", 4, 2, False),
    ])
    def test_list_views(self, app, chrome_driver, list_type, num_columns, num_rows, logged_in):
        
        # log in or log out
        if logged_in:
            self.log_in(chrome_driver)
        else:
            self.log_out(chrome_driver)

        get_url = f"{self.base_url}#{list_type}"

        chrome_driver.get(get_url)

        if list_type == 'projects':
            # Default view is card - switch to list.
            button = chrome_driver.find_element_by_id('toggle-list')
            button.click()

        # Get the jobs table. Will want to wait for this to be loaded,
        # of course.
        jobs_table = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, list_type))
        )

        # Check table dimensions.
        table_headings = jobs_table.find_elements_by_tag_name("th")
        table_rows = jobs_table.find_elements_by_tag_name("tr")

        #chrome_driver.get_screenshot_as_file(f'{list_type}_{logged_in}.png')

        assert len(table_headings) == num_columns
        assert len(table_rows) == num_rows

        # Check the response code of the links in the table.
        table_links = jobs_table.find_elements_by_class_name('nav-link')
        for link in table_links:
            # This is just a thing we have to do because of the way 'nav-links'
            # are handled in the app.
            important_url = link.get_attribute('href')[len(self.base_url):]
            actual_url = f'{self.base_url}/#{important_url}'
            response = requests.get(actual_url)
            assert response.status_code == 200
        
        # If we're not logged in we shouldn't see links (except for the public job)
        if not logged_in:
            if list_type == 'jobs':
                assert len(table_links) == 1
            else:
                assert len(table_links) == 0 

        #chrome_driver.get_screenshot_as_file(F'{list_type}_screenshot.png')

    def test_job_report_file_tree(self, app, chrome_driver, project_directory):
        """
        Test to make sure file tree loads with correct number of elements.
        """
        # Have to log in for this test
        self.log_in(chrome_driver)

        # Get page with chromedriver.
        chrome_driver.get(f"{self.base_url}#jobs/1")

        # Set up samples for comparison - we need the location of the job
        # which is in a temporary directory
        dir_path = os.path.dirname(os.path.realpath(__file__))
        test_dir = os.path.realpath(
            os.path.join(
                project_directory,
                "Job_000001"
            )
        )

        num_files = len(os.listdir(test_dir))

        # Get the file tree. Wait for a specific element to load so we know the
        # tree is loaded.
        file_tree = chrome_driver.find_element_by_id('js-tree')

        test_file = os.path.realpath(
            os.path.join(
                project_directory,
                "Job_000001", "job.out"
            )
        )

        test_file_id = urllib.parse.quote(test_file, safe='') + '_anchor'

        #chrome_driver.save_screenshot("screenshot.png")
        
        WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, test_file_id))
        )

        # Now get components.
        js_tree_contents = file_tree.find_elements_by_tag_name('li')

        num_files_in_tree = len(js_tree_contents)

        assert num_files_in_tree == num_files + 1

    def test_job_report_file_content(self, app, chrome_driver, project_directory):
        """
        Test to click file and make sure it is loaded into div.
        """
        # Have to log in for this
        self.log_in(chrome_driver)

        # Set up sample file for comparison.
        test_file = os.path.realpath(
            os.path.join(
                project_directory,
                "Job_000001", "job.out"
            )
        )

        with open(test_file) as f:
            file_contents = f.read()
            file_contents_split = file_contents.split()

        test_file_id = urllib.parse.quote(test_file, safe='') + '_anchor'

        chrome_driver.get(f"{self.base_url}#jobs/1")

        # Initially, there should be nothing in the text box.
        initial_displayed_text = chrome_driver.find_element_by_id(
            'file-content'
        ).text

        # Get a link for a file and click on it.
        job_link = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, test_file_id))
        )
        job_link.click()

        # When clicked, file text should be displayed in the div.
        displayed_text = chrome_driver.find_element_by_id('file-content').text

        displayed_text_list = displayed_text.split()

        # Splitting on whitespace and rejoining let's us compare the file
        # contents without worrying about how whitespace is handled.
        assert initial_displayed_text == ''
        assert ' '.join(displayed_text_list) == ' '.join(file_contents_split)

    def test_job_report_file_content_resize(self, app, chrome_driver, project_directory):
        """
        Test to make sure file content element resizes when next element is
        clicked.
        """

        #Make sure we're logged in
        self.log_in(chrome_driver)

        first_file = os.path.realpath(
            os.path.join(
                project_directory, "Job_000001", "job.out"
            )
        )
        second_file = os.path.realpath(
            os.path.join(
                project_directory, "Job_000001", "flowchart.flow"
            )
        )

        first_file_id = urllib.parse.quote(first_file, safe='') + '_anchor'
        second_file_id = urllib.parse.quote(second_file, safe='') + '_anchor'

        chrome_driver.get(f"{self.base_url}#jobs/1")

        # Get a link for a file and click on it.
        job_link = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, first_file_id))
        )
        job_link.click()

        flowchart_link = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, second_file_id))
        )
        flowchart_link.click()

        # File content div should not be displayed if another div is clicked on.
        assert not chrome_driver.find_element_by_id('file-content').is_displayed()
