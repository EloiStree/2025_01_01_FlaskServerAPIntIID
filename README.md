`Raspberrypi.local:8080`
[Service](http://raspberrypi.local:8080/services) | [Asym Client](http://raspberrypi.local:8080/asym-client) [C](https://github.com/EloiStree/2025_01_01_AsymmetricServerAPIntIID) |
[Trusted Client](http://raspberrypi.local:8080/trusted-client) [C](https://github.com/EloiStree/2025_01_01_TrustedServerAPIntIID)| [NTP Offset](http://raspberrypi.local:8080/ntp) [C](https://github.com/EloiStree/2025_01_01_HelloPiOsNtpServer)|
[IPV4](http://raspberrypi.local:8080/ipv4) | [Trusted Push IID](http://raspberrypi.local:8080/push_iid) |
[Reboot](http://raspberrypi.local:8080/reboot)  

-------------

# Flask Server APInt IID

A Flask Landing page for the Raspberry Pi that host some IID APInt feature and servers.




```
git clone https://github.com/EloiStree/2025_01_01_FlaskServerAPIntIID.git /git/apint_flask
```


```
sudo nano /etc/systemd/system/apint_flask.service
```

```
[Unit]
Description=APINT Flask Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /git/apint_flask/FlaskHost.py
WorkingDirectory=/git/apint_flask
Restart=always
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```
sudo nano /etc/systemd/system/apint_flask.timer
```

```
[Unit]
Description=Check APINT Flask Service every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=apint_flask.service

[Install]
WantedBy=timers.target
```


```
sudo nano /etc/systemd/system/apint_flask.service
sudo nano /etc/systemd/system/apint_flask.timer
systemctl daemon-reload
sudo systemctl enable apint_flask.service
sudo systemctl enable apint_flask.timer
sudo systemctl restart apint_flask.timer
sudo systemctl restart apint_flask.service

sudo systemctl status apint_flask.service
```





--------

```
crontab -e
```

```
@reboot /usr/bin/lxterminal -e "/usr/bin/chromium-browser --no-sandbox "/git/apint_flask/www/trusted/RunClient.html" & /usr/bin/chromium-browser --no-sandbox "/git/apint_flask/www/asymmetric/RunClient.html" 
```



