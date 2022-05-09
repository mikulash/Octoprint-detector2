# coding=utf-8
# Author: Mikulas Heinz, xheinz01, 2022, License: AGPLv3

from __future__ import absolute_import

import base64
import datetime

import octoprint.plugin
import octoprint.events
import octoprint.util



class Detector2Plugin(octoprint.plugin.SettingsPlugin,
                      octoprint.plugin.AssetPlugin,
                      octoprint.plugin.TemplatePlugin,
                      octoprint.plugin.StartupPlugin,
                      octoprint.plugin.EventHandlerPlugin
):

    def __init__(self):
        self._img_path = None
        self._snapshot_url =None

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
        self._snapshot_url = self._settings.global_get(['webcam', "snapshot"])
        if success:
            self._img_path = filename
            with open(filename, 'rb') as f:
                snap_two = f.read()
                snap_two = base64.encodebytes(snap_two)
            self._plugin_manager.send_plugin_message(self._identifier, dict(type="snap", time=currTime, img=snap_two))
            # self._logger.info("update sent")

    def get_assets(self):
        return {
            "js": ["js/detector2.js"],
            "json": ["js/graphMobileNetModel/model.json"],
            "css": ["css/detector2.css"],
        }
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "detector2": {
                "displayName": "Detector",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "mikulash",
                "repo": "OctoPrint-Detector2",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/mikulash/OctoPrint-Detector2/archive/{target_version}.zip",
            }
        }


# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Detector2 Plugin"
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Detector2Plugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.timelapse.capture.post": __plugin_implementation__.capture_post_handler
    }
