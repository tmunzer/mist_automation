

import time, sched
from queue import Queue
from threading import Thread
from time import time
import traceback
from flask import Flask
from flask import request
from datetime import datetime
from automation import trigger_webhooks
from libs.logger import Console
console = Console("http trig")


class HttpWorker(Thread):



    def __init__(self, server_port, webhook_uri, webhook_secret, automation_rules):
        Thread.__init__(self)
        self.server_port = server_port
        self.app = self._create_app(webhook_uri, webhook_secret, automation_rules)



    def _create_app(self, webhook_uri, webhook_secret, automation_rules):
        app = Flask(__name__)

        @app.route(webhook_uri, methods=["POST"])
        def postJsonHandler():
            console.info(" New message reveived ".center(60, "-"))
            start = datetime.now()

            res = trigger_webhooks.new_event(
                request,
                webhook_secret,
                automation_rules
            )
            delta = datetime.now() - start
            console.info(f"Processing time {delta.seconds}.{delta.microseconds}s")
            return res
        return app

    def run(self):
        try:
            print(f"Starting Server: 0.0.0.0:{self.server_port}".center(80, "_"))
            from waitress import serve
            serve(self.app, host="0.0.0.0", port=self.server_port)
        except Exception:
            console.critical("HTTP Server issue")
            traceback.print_exc()