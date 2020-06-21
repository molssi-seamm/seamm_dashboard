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

    def test_main_view(self, app, chrome_driver):
        chrome_driver.get(self.base_url)
        ui_view = chrome_driver.find_element_by_id("ui-view")
        displayed_values = ui_view.find_elements_by_class_name("text-value")
        expected_values = "0 2 0 1 1".split()
        displayed_values = [x for x in displayed_values if x != '']

        for i, value in enumerate(displayed_values):
            assert expected_values[i] == value.get_attribute('innerHTML')

    @pytest.mark.parametrize("list_type, num_columns, num_rows", [
        ("jobs", 7, 3),
        ("flowcharts", 5, 2),
        ("projects", 5, 2)
    ])
    def test_jobs_list(self, app, chrome_driver, list_type, num_columns, num_rows):
        chrome_driver.get(f"{self.base_url}#{list_type}")

        # Get the jobs table. Will want to wait for this to be loaded,
        # of course.
        jobs_table = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, list_type))
        )

        # Check table dimensions.
        table_headings = jobs_table.find_elements_by_tag_name("th")
        table_rows = jobs_table.find_elements_by_tag_name("tr")
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

        #chrome_driver.get_screenshot_as_file(F'{list_type}_screenshot.png')

    def test_job_report_file_tree(self, app, chrome_driver, project_directory):
        """
        Test to make sure file tree loads with correct number of elements.
        """
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

        # File content div should be 0 if another file type is selected.
        assert chrome_driver.find_element_by_id('file-content'
                                               ).size['height'] == 0
