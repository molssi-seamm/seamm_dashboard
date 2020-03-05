"""
Tests for the front end
"""

import urllib.request

from selenium.webdriver.common.by import By
from flask import request, url_for, Flask

from app import create_app
import pytest

import chromedriver_binary

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200

def test_jobs_list(client):
    # Need to figure out how to test that table is working.
    response = client.get('/#jobs', content_type="html/text", follow_redirects=True)
    assert response.status_code == 200



@pytest.mark.usefixtures('live_server')
class TestLiveServer:
    def test_main_view(app, selenium):
        selenium.get(url_for('main.index', _external=True))
        ui_view = selenium.find_element_by_id("ui-view")
        displayed_values = ui_view.find_elements_by_class_name("text-value")

        expected_values = "0 2 0 1 0".split()
        displayed_values = [x for x in displayed_values if x != '']

        for i,value in enumerate(displayed_values):
            print("hello",value.get_attribute('innerHTML'))
            assert expected_values[i] == value.get_attribute('innerHTML')
            
        #print('The page source is ', selenium.page_source)
        #print(ui_view.get_attribute('innerHTML'))