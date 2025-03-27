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


