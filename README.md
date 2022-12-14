# Mist Automation
Mist Automation is a small python app listening for Mist Webhooks to trigger automation.

It is composed of lightweight python web server ([Flask](https://github.com/pallets/flask)) and python code to process the webhook information and to automate action. The automation configuration is done with a YAML configuration file.

This script is available as is and can be run on any server with Python3. 

The script is also available as a Docker image. It is designed to simplify the deployment, and a script is available to automate the required images deployment.

## MIT LICENSE
 
Copyright (c) 2022 Thomas Munzer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the  Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# IMPORTANT
To get this script working, you will have to manually configure webhooks on your Mist account and enable the "audits", "alarms, "device-events" and/or "device-updowns" topics. This configuration can be done at the Organization level, or at the site level, depending on your needs.

This will tell Mist Cloud to send events (like AP Connected/Disconnected) to the Mist Automation server FQDN. As of today (January, 2020), some topics like the "device-events" topics cannot be enabled directly from the Mist UI. This configuration can be done through Mist APIs. You can use the web UI to manage APIs by reaching https://api.mist.com/api/v1/orgs/:your_org_id/webhooks or https://api.eu.mist.com/api/v1/orgs/:your_org_id/webhooks (Be sure to replace ":your_org_id" first). Then you will be able to create a new webhook by using the following settings:

```json
    {
        "url": "https://<mist_automation_server_fqdn>/<webhook_url>",
        "topics": [
            "device-events"
        ],
        "enabled": true
    }
```
# Features:
* Receive Webhooks from Mist (with or without Webhook Secret)
* Filter the webhook event based on the topic, the event type, or any field present in the event body
* Execute an automated action:
  * send a HTTP Request, with configurable headers and body (E.g. to automate configuration changes in Mist)
  * send the event top Slack or Teams


# How to use it
## Docker Image
You can easily deploy this application as a [Docker](https://www.docker.com/) image. The image is publicly available on Docker Hub at https://hub.docker.com/r/tmunzer/mist_automation/.
In this case, you can choose to manually deploy the image and create the container, or you can use the automation script (for Linux).

If you want to manually deploy the Docker image, the Mist Automation container will listen for HTTP messages on port `TCP51361`


When you are starting the script for the first time, it will ask some question:
##### Application FQDN
This parameter is very important, and the value must be resolvable by the HTTP clients. The script is deploying a NGINX containter in front of the application container. NGINX will be in charge to manage HTTPS connections, and to route the HTTP/HTTPS traffic to the right application (it is build to allow to run different applications on the same server). This routing is done based on the `host` parameter in the HTTP headers.

##### Permanent Folder
The script will automatically create a folder in the permanent folder you configured. This folder will be used to store permanent data from the application. The script will also generate a `config.py` file containing configuration example and help.

## Docker-Compose
You can find a docker-compose.yaml file in the root folder of the repository. This file can be used to quickly deploy the app without using the automation script.
Please note, in this case, you will have to manually generate all the required configuration files!

## Configuration
Before starting the Mist Automation application, you will have to configure it. To do so, edit the file `config.py`.

The file `config_example.py` contains the configuration structure with example values. 

You need to configure your Mist Organization to send Webhooks to this application.

