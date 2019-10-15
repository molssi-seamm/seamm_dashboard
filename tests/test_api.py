import requests


url = 'http://localhost:5000/api/search'
# url = 'http://localhost:5000/search'  # UI interface
headers = {'Content-Type': 'application/json'}


def test_empty_search():

    params = dict(query='', domain='[]', languages='["Python"]')
    response = requests.get(url, params=params, headers=headers)

    print(response.status_code)
    assert response.status_code == 200
    print(response.json())
