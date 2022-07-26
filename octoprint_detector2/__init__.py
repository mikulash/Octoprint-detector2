# coding=utf-8
# Author: Mikulas Heinz, xheinz01, 2022, License: AGPLv3

from __future__ import absolute_import

import base64
import datetime
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import octoprint.plugin
import octoprint.events
import octoprint.util
from octoprint.events import Events

import flask



class Detector2Plugin(octoprint.plugin.SettingsPlugin,
                        octoprint.plugin.AssetPlugin,
                        octoprint.plugin.TemplatePlugin,
                        octoprint.plugin.StartupPlugin,
                        octoprint.plugin.EventHandlerPlugin,
                        octoprint.plugin.SimpleApiPlugin,
                      ):

    def __init__(self):
        self._img_path = None
        self.data = None

    # user settings
    def on_after_startup(self):
        self._logger.info("|||||||||||||||DETECTOR 2 STARTED!||||||||||||||||\||")

    def get_settings_defaults(self):
        return {
            "host": "smtp.office365.com",
            "username": "your new outlook mail",
            "password": base64.b64encode("default password".encode("utf-8")),
            "port": 587,
            "to": "your personal mail",
            "confidence": 75
        }

    def on_settings_save(self, data):
        self._plugin_manager.send_plugin_message(self._identifier, dict(type="userChange", data=data))
        if ("password" in data):
            data["password"] = base64.b64encode(data.get("password").encode("utf-8"))
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

    def on_settings_load(self):
        data = octoprint.plugin.SettingsPlugin.on_settings_load(self)
        data["password"] = base64.b64decode(data.get("password"))
        self._plugin_manager.send_plugin_message(self._identifier, dict(type="userChange", data=data))
        octoprint.plugin.SettingsPlugin.on_settings_load(self)
        self.data = data
        return data

    def get_template_configs(self):
        return [
            dict(type="tab", custom_bindings=False),
            dict(type="settings", custom_bindings=False)
            ]

    # snapshot taken hook
    def capture_post_handler(self, filename, success):
        currTime = datetime.datetime.now().strftime("%H:%M:%S")
        if success:
            self._img_path = filename
            with open(filename, 'rb') as f:
                snap_two = f.read()
                snap_two = base64.encodebytes(snap_two)
            self._plugin_manager.send_plugin_message(self._identifier, dict(type="snap", time=currTime, img=snap_two, filepath=filename))

    def register_custom_events(*args, **kwargs):
        return ["error_found"]

    def send_error_found_event(self, data):
        event = Events.PLUGIN_DETECTOR2_ERROR_FOUND
        custom_payload = dict(errorType=data['errorType'], confidence=data['confidence'])
        self._event_bus.fire(event, payload=custom_payload)

    # def on_event(self, event, payload):
    #     # testing event emiting
    #     if event == Events.PLUGIN_DETECTOR2_ERROR_FOUND:
    #         self._logger.info("on event {}".format(payload))

    def on_api_get(self, request):
        self.send_error_found_event(request.args)
        self.sendEmail(request.args)
        return flask.jsonify(foo="bar")

    def get_assets(self):
        return {
            "js": ["js/detector2.js"],
            "json": ["js/graphMobileNetModel/model.json"],
            "css": ["css/detector2.css"],
        }

    def get_update_information(self):
        return {
            "detector2": {
                "displayName": "Detector",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "mikulash",
                "repo": "OctoPrint-Detector2",
                "current": self._plugin_version,
                "pip": "https://github.com/mikulash/OctoPrint-Detector2/archive/{target_version}.zip",
            }
        }

    def sendEmail(self, content):
        data = self.data
        password = data['password'].decode('utf-8')
        smtp_server = data['host']
        sender_email = data['username']
        receiver_email = data['to']
        message = "Error type: {} with confidence of {} %.".format(content['errorType'], content['confidence'])
        with open(self._img_path, 'rb') as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename=error.jpg",
        )
        self._logger.info(message)
        part1 = MIMEText(message, "plain")
        message = MIMEMultipart()
        message["Subject"] = "Error was found during printing"
        message["From"] = data['username']
        message["To"] = data['to']
        message.attach(part1)
        message.attach(part)
        context = ssl.create_default_context()
        try:
            server = smtplib.SMTP(smtp_server, data['port'])
            server.starttls(context=context)  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.close()
        except Exception as e:
            self._logger.info(" mail exception {}".format(e))


__plugin_name__ = "Detector2 Plugin"
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Detector2Plugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.timelapse.capture.post": __plugin_implementation__.capture_post_handler,
        "octoprint.events.register_custom_events": __plugin_implementation__.register_custom_events,
    }
