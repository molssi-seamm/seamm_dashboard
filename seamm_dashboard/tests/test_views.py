"""
Tests for the front end
"""

from flask import url_for

import pytest
import requests
import os
import platform
import sys
import time

import urllib.parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Needed for Python 3.8 since default for OS/X changed to spawn rather than
# fork.
if sys.version_info >= (3, 8) and platform.system() == "Darwin":
    import multiprocessing

    multiprocessing.set_start_method("fork")


@pytest.mark.usefixtures("live_server")
class TestLiveServer:
    """
    This uses selenium and the 'live_server' fixture which comes with
    pytest-flask.
    """

    @property
    def base_url(self):
        return url_for("main.index", _external=True)

    def log_in(self, chrome_driver, username="sample_user", password="sample_password"):
        """
        Function to log sample user in for testing.
        """
        login_url = f"{self.base_url}/login"
        chrome_driver.get(login_url)

        username_field = chrome_driver.find_element_by_id("username")
        username_field.send_keys(username)

        username_field = chrome_driver.find_element_by_id("password")
        username_field.send_keys(password)

        button = chrome_driver.find_element_by_id("submit")
        button.click()

        # For some reason we need to navigate away from the main page
        # before loading the page of interest or we time out
        chrome_driver.get(f"{self.base_url}api/status")

    def log_out(self, chrome_driver):
        """
        Function to make sure we are logged out
        """

        logout_url = f"{self.base_url}/logout"

        chrome_driver.get(logout_url)

    @pytest.mark.parametrize("logged_in", [True, False])
    def test_main_view(self, app, chrome_driver, logged_in):

        if logged_in:
            self.log_in(chrome_driver)
            # Should have three finished jobs, 1 flowchart, and 1 project when
            # logged in.
            expected_values = "3 0 3 1 1".split()

        else:
            # Make sure we are logged out
            self.log_out(chrome_driver)
            # Should have one public job and nothing else.
            expected_values = "1 0 1 0 0".split()

        chrome_driver.get(self.base_url)
        # chrome_driver.get_screenshot_as_file(f'main_{logged_in}.png')
        ui_view = chrome_driver.find_element_by_id("ui-view")
        displayed_values = ui_view.find_elements_by_class_name("text-value")

        displayed_values = [x for x in displayed_values if x != ""]

        for i, value in enumerate(displayed_values):
            assert expected_values[i] == value.get_attribute("innerHTML")

    @pytest.mark.parametrize(
        "list_type, num_columns, num_rows, logged_in",
        [
            ("jobs", 7, 4, True),
            ("jobs", 7, 2, False),
            ("flowcharts", 5, 2, True),
            ("flowcharts", 5, 2, False),
            ("projects", 4, 2, True),
            ("projects", 4, 2, False),
        ],
    )
    def test_list_views(
        self, app, chrome_driver, list_type, num_columns, num_rows, logged_in
    ):

        # log in or log out
        if logged_in:
            self.log_in(chrome_driver)
        else:
            self.log_out(chrome_driver)

        get_url = f"{self.base_url}#{list_type}"

        # Get twice just to make sure this request goes through.
        chrome_driver.get(get_url)
        chrome_driver.get(get_url)

        if list_type == "projects":
            # Default view is card - switch to list.
            button = chrome_driver.find_element_by_id("toggle-list")
            button.click()

        # chrome_driver.get_screenshot_as_file(f'{list_type}_{logged_in}.png')

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
        table_links = jobs_table.find_elements_by_class_name("nav-link")
        for link in table_links:
            # This is just a thing we have to do because of the way 'nav-links'
            # are handled in the app.
            important_url = link.get_attribute("href")[len(self.base_url) :]
            actual_url = f"{self.base_url}/#{important_url}"
            response = requests.get(actual_url)
            assert response.status_code == 200

        # If we're not logged in we shouldn't see links (except for the public job)
        if not logged_in:
            if list_type == "jobs":
                assert len(table_links) == 1
            else:
                assert len(table_links) == 0

        # chrome_driver.get_screenshot_as_file(F'{list_type}_screenshot.png')

    @pytest.mark.xfail
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
        test_dir = os.path.realpath(os.path.join(project_directory, "Job_000001"))

        num_files = len(os.listdir(test_dir))

        # Get the file tree. Wait for a specific element to load so we know the
        # tree is loaded.
        file_tree = chrome_driver.find_element_by_id("js-tree")

        test_file = os.path.realpath(
            os.path.join(project_directory, "Job_000001", "job.out")
        )

        test_file_id = urllib.parse.quote(test_file, safe="") + "_anchor"

        WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, test_file_id))
        )

        # Now get components.
        js_tree_contents = file_tree.find_elements_by_tag_name("li")

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
            os.path.join(project_directory, "Job_000001", "job.out")
        )

        with open(test_file) as f:
            file_contents = f.read()
            file_contents_split = file_contents.split()

        test_file_id = urllib.parse.quote(test_file, safe="") + "_anchor"

        chrome_driver.get(f"{self.base_url}#jobs/1")

        # Initially, there should be nothing in the text box.

        initial_displayed_text = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, "file-content"))
        ).text

        # Get a link for a file and click on it.
        job_link = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, test_file_id))
        )
        job_link.click()

        # Give time to load
        time.sleep(0.25)

        # When clicked, file text should be displayed in the div.
        displayed_text = chrome_driver.find_element_by_id("file-content").text

        displayed_text_list = displayed_text.split()

        # Splitting on whitespace and rejoining let's us compare the file
        # contents without worrying about how whitespace is handled.
        assert initial_displayed_text == "", "initial displayed text error"
        assert " ".join(displayed_text_list) == " ".join(file_contents_split), "displayed text error"

    def test_job_report_file_content_refresh(
        self, app, chrome_driver, project_directory
    ):
        """
        Test to click file and make sure it is loaded into div.
        """
        # Have to log in for this
        self.log_in(chrome_driver)

        # Set up sample file for comparison.
        test_file = os.path.realpath(
            os.path.join(project_directory, "Job_000001", "job.out")
        )

        with open(test_file) as f:
            file_contents = f.read()
            file_contents_split = file_contents.split()

        test_file_id = urllib.parse.quote(test_file, safe="") + "_anchor"

        chrome_driver.get(f"{self.base_url}#jobs/1")

        # Initially, there should be nothing in the text box.
        initial_displayed_text = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, "file-content"))
        ).text

        # Get a link for a file and click on it.
        job_link = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.ID, test_file_id))
        )
        job_link.click()

        time.sleep(0.10)

        # When clicked, file text should be displayed in the div.
        displayed_text = chrome_driver.find_element_by_id("file-content").text

        displayed_text_list = displayed_text.split()

        # Splitting on whitespace and rejoining let's us compare the file
        # contents without worrying about how whitespace is handled.
        assert initial_displayed_text == ""
        assert " ".join(displayed_text_list) == " ".join(
            file_contents_split
        ), "initial load failed."

        # Update file on disk
        with open(test_file, "a+") as f:
            f.write("Appending this line")

        # Update expected text
        file_contents_split += "Appending this line".split()

        # Click refresh button
        refresh_button = chrome_driver.find_element_by_id("refresh")
        refresh_button.click()
        time.sleep(0.10)

        # Check the new displayed text
        new_displayed_text = chrome_driver.find_element_by_id("file-content").text
        new_displayed_list = new_displayed_text.split()

        assert " ".join(new_displayed_list) == " ".join(file_contents_split)

    def test_job_report_file_content_resize(
        self, app, chrome_driver, project_directory
    ):
        """
        Test to make sure file content element resizes when next element is
        clicked.
        """

        # Make sure we're logged in
        self.log_in(chrome_driver)

        first_file = os.path.realpath(
            os.path.join(project_directory, "Job_000001", "job.out")
        )
        second_file = os.path.realpath(
            os.path.join(project_directory, "Job_000001", "flowchart.flow")
        )

        first_file_id = urllib.parse.quote(first_file, safe="") + "_anchor"
        second_file_id = urllib.parse.quote(second_file, safe="") + "_anchor"

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
        assert not chrome_driver.find_element_by_id("file-content").is_displayed()

    def test_admin_views_logged_out(self, app, chrome_driver):
        """
        Make sure admin views are protected
        """

        # Make sure we're logged out
        self.log_out(chrome_driver)

        # Try to access admin views - manage_users page
        chrome_driver.get(f"{self.base_url}/admin/manage_users")

        header = chrome_driver.find_elements_by_tag_name("h1")[0]

        assert header.text == "401"

        # Try to access admin views - create users page
        chrome_driver.get(f"{self.base_url}/admin/create_user")

        header = chrome_driver.find_elements_by_tag_name("h1")[0]

        assert header.text == "401"

    def test_admin_create_user(self, app, chrome_driver):

        # Make sure we're logged in as admin
        self.log_in(chrome_driver, username="admin_user", password="iamadmin")

        # Try to access admin views - manage_users page
        chrome_driver.get(f"{self.base_url}/admin/create_user")

        username_field = chrome_driver.find_element_by_id("username")
        username_field.send_keys("new_user")

        password_field = chrome_driver.find_element_by_id("password")
        password_field.send_keys("test_password")

        password2_field = chrome_driver.find_element_by_id("password2")
        password2_field.send_keys("test_password")

        firstname_field = chrome_driver.find_element_by_id("first_name")
        firstname_field.send_keys("FirstName")

        lastname_field = chrome_driver.find_element_by_id("last_name")
        lastname_field.send_keys("LastName")

        email_field = chrome_driver.find_element_by_id("email")
        email_field.send_keys("email@email.com")

        button = chrome_driver.find_element_by_id("submit")
        button.click()

        # Check that alert is found. If not found will result in error.
        chrome_driver.find_element_by_class_name("alert-success")

        table_rows = chrome_driver.find_element_by_id(
            "users"
        ).find_elements_by_tag_name("tr")

        # chrome_driver.get_screenshot_as_file(f'user_table.png')

        assert len(table_rows) == 7

    def test_admin_edit_user(self, app, chrome_driver):

        # Make sure we're logged in as admin
        self.log_in(chrome_driver, username="admin_user", password="iamadmin")

        # Try to access admin views - manage_users page
        chrome_driver.get(f"{self.base_url}/admin/manage_user/1")

        # chrome_driver.get_screenshot_as_file(f'updated_user.png')

        edit_button = chrome_driver.find_elements_by_css_selector(
            "#user-information-button .btn"
        )[0]
        edit_button.click()

        # chrome_driver.get_screenshot_as_file(f'updated_user_after_after_click.png')

        # with open('page_source.html', 'w+') as f:
        #    f.write(chrome_driver.page_source)

        firstname_field = chrome_driver.find_element_by_id("first_name")
        firstname_field.send_keys("FirstName")

        lastname_field = chrome_driver.find_element_by_id("last_name")
        lastname_field.send_keys("LastName")

        email_field = chrome_driver.find_element_by_id("email")
        email_field.send_keys("changed_address@email.com")

        # chrome_driver.get_screenshot_as_file(f'updated_user.png')

        button = chrome_driver.find_element_by_id("submit")
        button.click()

        chrome_driver.find_element_by_class_name("alert-success")
        # chrome_driver.get_screenshot_as_file(f'user_table.png')
