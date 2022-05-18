# coding=utf-8
# Author: Mikulas Heinz, xheinz01, 2022, License: AGPLv3

from __future__ import absolute_import

import base64
import datetime

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

    # user settings
    def on_after_startup(self):
        self._logger.info("DETECTOR 2 STARTED!")

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
        return data

    def get_template_configs(self):
        return [
            dict(type="tab", custom_bindings=False),
            dict(type="settings", custom_bindings=False)
            ]

    # snapshot taken hook
    def capture_post_handler(self, filename, success):
        # self._logger.info("Post handler success: {}, filename: {}".format(success, filename))
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

    def on_event(self, event, payload):
        # testing event emiting
        if event == Events.PLUGIN_DETECTOR2_ERROR_FOUND:
            self._logger.info("on event {}".format(payload))

    def on_api_get(self, request):
        self.send_error_found_event(request.args)
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
