Everyone Panic!
===============

This is an easy way to set up a monitoring system that calls your phone number
if any of your websites go down. It uses Uptime Robot for continual
monitoring and Twilio for voice calls. You can set it up to call multiple
phone numbers as well.

It's almost free! You will have to pay for each voice call at the Twilio voice
rate ($0.02 per call per callee in the USA).

It should be easy to set up on either App Engine or Heroku. Obviously, you
should use a hosting platform that isn't also used for your sites.

It's the closest thing we've had to a "set it and forget it" service, since we
don't need to touch it in order to add additional sites in Uptime Robot. This
app has been dutifully watchful for us ever since we whipped it up one day,
and since our automated monitoring has grown a lot more since then, we figured
that it was time to release it into the wild.


Configuration
-------------

You need to add in a few different environment variables, either through the
`app.yaml` file or through `heroku config`:

* `application` - change "my_app_name" to your App Engine name
* `APP_HOSTNAME` - required for Heroku, tries to detect it on App Engine
* `TWILIO_SID` - find this in your Twilio account
* `TWILIO_TOKEN` - also find this in your Twilio account
* `TWILIO_FROM` - a Twilio purchased or validated phone number
* `CALLEES` - a comma separated list of phone numbers:
`+15551111111,+15552222222'
* `UPTIME_ROBOT_KEY` - your Uptime Robot account's API key


Cron job
--------

The app checks Uptime Robot every 15 minutes (by default) but needs to be
triggered from a specific URL. A `cron.yaml` file is provided for App Engine.
If you use Heroku, one way to do it is to have Uptime Robot check to see if
`http://your_app_name.herokuapp.com/checksites` is up every 15 minutes.
Another way is to use the Heroku Scheduler.

We've found that 15 minutes is a decent value that keeps the app in the free
tier of App Engine and would miss most transient outages that we see via other
means anyways.


Deployment
----------

If you're using App Engine, you'll first have to pull down the libraries
locally. Running `pip install -r requirements.txt` should do the trick.
Since `webapp2` is included with App Engine, you can delete that from
requirements.txt or delete the module after it has downloaded.
Then, you need to edit the values in `app.yaml` to reflect your app. Once
that's done, you can just push it up to App Engine.

If you're using Heroku, you need to use `heroku config` to set each
environment variable as described above. Then, you can deploy the app to
Heroku and set up a cron job as described above.
