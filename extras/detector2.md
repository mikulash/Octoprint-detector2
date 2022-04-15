---
layout: plugin

id: detector2
title: OctoPrint-Detector2
description: Detect error locally in your browser and sends email with detected error
authors:
- Mikulas Heinz
license: AGPLv3

# TODO
date: 2022-04-15

homepage: https://github.com/mikulash/OctoPrint-Detector2
source: https://github.com/mikulash/OctoPrint-Detector2
archive: https://github.com/mikulash/OctoPrint-Detector2/archive/master.zip

# TODO
# Set this to true if your plugin uses the dependency_links setup parameter to include
# library versions not yet published on PyPi. SHOULD ONLY BE USED IF THERE IS NO OTHER OPTION!
#follow_dependency_links: false

# TODO
tags:
- ai
- alerts
- automation
- defect detection
- email
- failure
- monitoring
- notifications
- local

# TODO
screenshots:
- url: /assets/img/plugins/OctoPrint-Detector2/mailPreview.png
  alt: received email
  caption: Email sent from plugin
- url: /assets/img/plugins/OctoPrint-Detector2/OctoprintPreview.png
  alt: octoprint integration
  caption: as tab in octoprint
- url: /assets/img/plugins/OctoPrint-Detector2/settingsPreview.png
  alt: filling out the settings
  caption: Settings page

# TODO
featuredimage: url of a featured image for your plugin, /assets/img/...

# TODO
# You only need the following if your plugin requires specific OctoPrint versions or
# specific operating systems to function - you can safely remove the whole
# "compatibility" block if this is not the case.

compatibility:

  # List of compatible versions
  #
  # A single version number will be interpretated as a minimum version requirement,
  # e.g. "1.3.1" will show the plugin as compatible to OctoPrint versions 1.3.1 and up.
  # More sophisticated version requirements can be modelled too by using PEP440
  # compatible version specifiers.
  #
  # You can also remove the whole "octoprint" block. Removing it will default to all
  # OctoPrint versions being supported.

  octoprint:
  - 1.4.0

  # List of compatible operating systems
  #
  # Valid values:
  #
  # - windows
  # - linux
  # - macos
  # - freebsd
  #
  # There are also two OS groups defined that get expanded on usage:
  #
  # - posix: linux, macos and freebsd
  # - nix: linux and freebsd
  #
  # You can also remove the whole "os" block. Removing it will default to all
  # operating systems being supported.

  os:
  - linux
  - windows
  - macos
  - freebsd

  # Compatible Python version
  #
  # It is recommended to only support Python 3 for new plugins, in which case this should be ">=3,<4"
  #
  # Plugins that wish to support both Python 2 and 3 should set it to ">=2.7,<4".
  #
  # Plugins that only support Python 2 will not be accepted into the plugin repository.

  python: ">=3,<4"

---
Octoprint-Detector2 is a detection plugin that runs in locally your browser and emails you if it detects some spaghetti, stringing or blobs on your print. All you need is an email account and a PC.
That means it is completely free without any monthly subscriptions or one time fees. If it detects an error it sounds the alarm and sends you an email with the latest image of the print.

### setup
Install via the Plugin Manager or manually using this URL:
Uses Tensorflow.js for prediction, https://www.smtpjs.com/ to send mail via javascript and Outlook to serve as an SMTP server.

## Configuration

1. To enable email sending it needs to use an SMTP connection. Free and easy to set up is via Outlook. For now, this plugin uses exclusively Outlook so at this moment there is no need for extra set-up. Just creating an email will do it.
2. In the settings of this plugin enter the username and password for created Outlook account.
3. This plugin uses snapshots sent by the Timelapse plugin, which is preinstalled with Octoprint. Go to the Timelapse tab and choose snapshot interval. The minimal recommended interval is 10 seconds to let the plugin have enough time to detect errors from an image.
4. Once you start printing you should see the last sent image and result that this detector gets as well with confidence of the result.
5. If the confidence of the error is greater than 75 %. It starts the alarm and sends you an email. Email is sent exactly once to prevent spamming.
6. That’s it. You just need to leave the octoprint tab running in the browser and let it work.

## Q&A
Email sending stopped working.
To prevent spamming, Outlook has a daily limit for services like this. Open the Outlook account and you should have received a prompt to verify this account. After verification you should be able to start receiving email again.

## problems or feedback?
If you are having any trouble or have an idea to implement, let me know! This plugin is part of my bachelor thesis so any feedback would be much appreciated.
