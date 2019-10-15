## Deployment Options

### 1. Ngrok for a Quick demo (10 users' access):

* Run the app locally: `python molssi_api_flask.py`
* on a different shell, tell ngrok to route to your app: `ngrok http 5000`
* Will return the temp URL for others to access on the cloud.

Note: URL changes each time you run ngrok. 
Connection is lost when you close your machine or shut down the local development server.

### 2. Heroku

* Create a Procfile with
`web: gunicorn molssi_api_flask:app --log-file -
`
* Download the heroku app
* Run on shell
  ```
  cd path/to/project
  heroku create app_name
  git remote -v
  git push heroku master   # push, install requiremnts.txt, run server
  heroku config:set FLASK_CONFIG=production   # set env variables ...
  heroku open              # open the website in the browser
  ``` 
 
 Notes: fastest and easiest way to get an app up on the cloud for free. 
 Scaling is a bit pricey.
 
 ### 3. Serverless
 
 Unlike other platform services, you app process is not running all the time. 
 The app process is sleeping but quickly run once a request is sent to it.
 Serverless available from most big cloud providers, e.g., AWS Lambda, Azur, Google Engine.
 Example here to deploy of AWS Lambda using a python wrapper, zappa, for easier deployment.
 
 * Create an AWS Lambda account
 * run
    ```
    cd path/to/project
    pip install zappa
    zappa init 
    ```
 * Answer questions: name of environment (e.g. production), personal, pass, 
 path to flask app, deploy globally (if yes, costs more).
 * deploy the environment `zappa deploy production`
 * after installing dependencies and running, it will output the app url
 
 Note: Good cost for small to medium loads. 
 Takes care of scalling if you have spiky traffic. Not easy to debug.
 
 ### 4. Virtual Machines
 
 Used by most big organizations. Many providers available.
 Example: Google cloud plateform.
 
 * create an acoount on Google cloud
 * create a VM in the Compute Engine (pay after free trial)
 * Copy the gcloud ssh command from the ssh drop down (under connect column)
 * download and install gcloud as in their instructions
 * Use your local shell to run:
    ```
    gcloud auth login    # then login
    gcloud compute --project "molssi-cms-db" ssh --zone "us-east1-b" "instance-1"
    ```
 * After logging in to the VM, setup your server for the app:
    ```
    sudo su
    apt-get install python-pip
    pip install virtualenv
    cd /var
    virtualenv -p python3 venv
    source venv/bin/activate
    git clone https://github.com/doaa-altarawy/molssi_api_flask.git
    pip install -r requirements.txt   
    ``` 
 * Run a gunicorn server from shell. 
 Note that it's by default listening to port 8000 only from local host, 
 so we need to make it listen on port 80 and from the internet. So run on shell:
     ```
     pip install gunicorn
     gunicorn molssi_api_flask:app --log-file - --bind 0.0.0.0:80
     ```
 * Get the URL of this VM from the google cloud platform
 
 Note: Free control but more work for configuration and monitoring.
 
 
 ## 5. Docker
 Good control but less overhead than a full VM.
 
 * Create a Dockerfile inside your project tree. Sample content:
    ```
     FROM python:3.5-onbuild
     EXPOSE 5000
     CMD gunicorn molssi_api_flask:app --log-file - --bind 0.0.0.0:5000
    ```
 * Install Docker, then build and run the container:
    ```
    cd path/to/project
    docker build -t daltarawy/molssi_db .   # tag name for the container, {your_namespace}/{proj_name}
    docker run -p 5000:5000 daltarawy/molssi_db    # expose port 5000 from container into 5000 in host
    docker container ls --all
    docker stop container_ID    # not tag
    ```
 * Push to docker hub
    ```
    docker login
    docker push daltarawy/molssi_db
    ```
 * Then on your depolyment server, install docker and then run
     ```
     docker pull daltarawy/molssi_db
     docker run -p 5000:5000 daltarawy/molssi_db    # not tested yet
     ```
 
 
 Note: This project will have approx 60MB docker container.
 
 **Note**: DB accesses a cloud DB on mLab. 
 More setup is needed for a mongoDB docker container.
  
 
 