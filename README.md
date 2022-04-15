# OctoPrint-Detector2

**TODO:** Describe what your plugin does.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/mikulash/OctoPrint-Detector2/archive/master.zip

Octoprint-Detector2 is a detection plugin that runs in locally your browser and emails you if it detects some spaghetti, stringing or blobs on your print. All you need is an email account and a PC.
That means it is completely free without any monthly subscriptions or one time fees. If it detects an error it sounds the alarm and sends you an email with the latest image of the print.

Uses Tensorflow.js for prediction, https://www.smtpjs.com/ to send mail via javascript and Outlook to serve as an SMTP server.

## Configuration

1. To enable email sending it needs to use an SMTP connection. Free and easy to set up is via Outlook. For now, this plugin uses exclusively Outlook so at this moment there is no need for extra set-up. Just creating an email will do it.
2. In the settings of this plugin enter the username and password for created Outlook account.
3. This plugin uses snapshots sent by the Timelapse plugin, which is preinstalled with Octoprint. Go to the Timelapse tab and choose snapshot interval. The minimal recommended interval is 10 seconds to let the plugin have enough time to detect errors from an image.
4. Once you start printing you should see the last sent image and result that this detector gets as well with confidence of the result.
5. If the confidence of the error is greater than 75 %. It starts the alarm and sends you an email. Email is sent exactly once to prevent spamming.
6. That’s it. You just need to leave the octoprint tab running in the browser and let it work.

## Q&A
#### Email sending stopped working.
To prevent spamming, Outlook has a daily limit for services like this. Open the Outlook account and you should have received a prompt to verify this account. After verification you should be able to start receiving email again.

## problems or feedback?
If you are having any trouble or have an idea to implement, let me know! This plugin is part of my bachelor thesis so any feedback would be much appreciated. Reach me at discussion in this plugin github repository
https://github.com/mikulash/Octoprint-detector2/discussions
