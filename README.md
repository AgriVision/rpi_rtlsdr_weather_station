# rpi_rtlsdr_weather_station

rpi_rtlsdr_weather_station provides  python code, based on https://dash.plotly.com to show weather data from a wireless weather station to a web page, served from a raspberry pi. Wireless data from the weather station is received with a RTL-SDR dongle and decoded by https://github.com/merbanan/rtl_433/.

The code is tested with a Fine Offset Electronics WH1080/WH3080 compatible Weather Station (Alecto WS-4000)

![Alecto WS-4000](./images/ws4000.png)

## The setup consists of two python scripts:
* <span>ws2sqlite.py</span> (pipes weather data from rtl_433 to a sqlite database)
* show_weather_station.py (serves a web page graphing data from the sqlite database using Dash.plotly)

## Installation
Open the crontab editor:
```
sudo crontab -e
```
Add the folowing lines to your crontab:

```
# weather station logger
0,10,20,30,40,50 * * * *        /usr/local/bin/rtl_433 -p 69 -f 868M -F json -R 155 -T 90 -E quit | /usr/bin/python /home/pi/bin/ws2sqlite.py >> /var/log/temperature/ws_error.log
```
The command is executed at an interval of 10 minutes. This interval was choosen in order not to overload the raspberry pi (rtl_433 takes 30% cpu on a raspberry pi 2) and still provide sufficient data to plot.

The rtl_433 options used are:
Option | Description
------ | ------
-p 69 | to compensate the ppm error (tested with rtl_test -p) 
-f 868M | 868 MHz is the frequency used at the WS-4000
-F json | output json format
-R 155 | only output protocol 155 (Fine Offset Electronics WH1080/WH3080 Weather Station (FSK))
-T 90 | timeout if nothing received in 90 seconds
-E quit | quit command after successful event

The output (json data) is piped to the <span>ws2sqlite.py</span> script, which saves the data in a sqlite database.

## Web server 

The show_weather_station.py python script extracts the saved weather data from the sqlite database and displays nice graphs in a web browser. Dash.plotly is the framework used for this. A Dash DatePickerRange is used at the bottom of the page to select the dates for which the weather data is plotted. In this example the internal DASH webserver is used, but Dash can also be used in connection with your standard raspberri pi webserver such as apache2. When running standalone the web page is served at port 8050.


```
python3 rpi_rtlsdr_weather_station/show_weather_station.py
```

```
2.0.0
Dash is running on http://0.0.0.0:8050/

 * Serving Flask app 'show_weather_station' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://192.168.2.212:8050/ (Press CTRL+C to quit)
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-layout HTTP/1.1" 200 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-dependencies HTTP/1.1" 200 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-component-suites/dash/dcc/async-graph.js HTTP/1.1" 304 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-component-suites/dash/dcc/async-datepicker.js HTTP/1.1" 304 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-component-suites/dash/dcc/async-plotlyjs.js HTTP/1.1" 304 -
127.0.0.1 - - [30/Nov/2021 20:16:18] "POST /_dash-update-component HTTP/1.1" 200 -
```

Add the command to /etc/rc.local if you want the application to start automatically at rpi boot time.
```
# show weather station logs in dash application
python3 /home/pi/rpi_rtlsdr_weather_station/show_weather_station.py >> /var/log/show_weather_station.log 2>&1 &
```
That's it!