
## pip install flask markdown --break-system-packages

bool_allows_to_reboot = False
bool_allows_to_reboot = True

import os
import socket
import struct
import sys

import markdown

if sys.stdout.isatty():
    print("Running in a terminal.")
    stop_service_script ="""
    sudo systemctl stop apint_flask.service
    sudo systemctl stop apint_flask.timer
    """

    # run code to stop current service
    os.system(stop_service_script)

else:
    print("Not running in a terminal.")



from flask import Flask, jsonify, render_template, request
import subprocess
import os
import ntplib
from datetime import datetime, timezone
import time

app = Flask(__name__,template_folder=os.path.dirname(os.path.abspath(__file__)))


services = [
    "ntp",
    "apint_asym_push_iid.service",
    "apint_asym_push_iid.timer",
    "apint_trusted_push_iid.service",
    "apint_trusted_push_iid.timer",
    "apint_udp_relay_iid.service",
    "apint_udp_relay_iid.timer",
    "apint_flask.service",
    "apint_flask.timer",
    "apint_client_pyjs.service",
    "apint_client_pyjs.timer"
]

def get_service_status(service):
    try:
        result = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        status = result.stdout.strip()
        return status
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def home():
    return serve_page("welcome")

@app.route('/asym-client')
def asym_client():
    return render_template("www/asymmetric/RunClient.html")

@app.route('/trusted-client')
def trusted_client():
    return render_template("www/trusted/RunClient.html")

def redirect_to(url):
    return f'<html><head><meta http-equiv="refresh" content="0;url={url}" /></head><body></body></html>'

@app.route('/help')
def help():
    return redirect_to("https://github.com/EloiStree")

@app.route('/discord')
def discord():
    return redirect_to("https://discord.gg/uKwNN2ECJH")

@app.route('/donation')
def donation():
    return redirect_to("https://buymeacoffee.com/apintio")

@app.route('/source')
def source():
    return redirect_to("https://github.com/EloiStree/2025_01_01_FlaskServerAPIntIID.git")


@app.route('/asym/rsa4096')
def generate_rsa4096_key():
    return render_template("www/asymmetric/GenerateRSA4096.html")

@app.route('/asym/rsa512')
def generate_rsa512_key():
    return render_template("www/asymmetric/GenerateRSA512.html")

@app.route('/asym/ecc')
def generate_rsaecc_key():
    return render_template("www/asymmetric/GenerateECC.html")

@app.route('/rtfm')
def rtfm():
    return serve_page("rtfm")


def load_markdown_file(filename):
    """Loads a Markdown file, converts it to HTML, and returns it."""
    file_path = os.path.join("www/md/", filename)
    
    if not os.path.exists(file_path):
        return "<h1>404 - Page Not Found</h1><p>The requested page does not exist.</p>"

    with open(file_path, "r", encoding="utf-8") as file:
        md_content = file.read()
    return markdown.markdown(md_content)

@app.route("/md/<page>")
def serve_page(page):
    html_content = load_markdown_file(f"{page}.md")
    html = render_template("www/template/markdown_page.html")
    html = html.replace("#BODYMARKDOWNHERE#", html_content)
    html = html.replace("#TITLE#", page)
    
    return html



def replace_body_in_default_html(body):
    html_page_to_load= "www/template/insert_body_here.html"
    html_template = open(html_page_to_load).read()
    html_template = html_template.replace("BODY", body)
    return html_template

@app.route('/services')
def services_route():
    service_statuses = {service: get_service_status(service) for service in services}
    #unpack  the json to make it more readyable in html
    html_services = """
    <table border="1" style="width:100%; text-align:left;">
        <thead>
            <tr>
                <th>Service</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
    """
    for service, status in service_statuses.items():
        color = "green" if status == "active" else "red"
        html_services += f"<tr><td>{service}</td><td style='color:{color};'>{status}</td></tr>"
    html_services += """
        </tbody>
    </table>
    """
    return replace_body_in_default_html(html_services)





def get_raspberry_pi_serial():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    return line.split(":")[1].strip()
    except Exception as e:
        print(f"Error reading serial: {e}")
    return os.popen("hostname").read().strip()


import os
hostname=""
hostname_ip=""
hostname_ips=""
hostname_unique_id=""
def refresh_hostname():
    global hostname_ip, hostname, hostname_ips, hostname_unique_id
    if hostname_ip==None or hostname_ip=="":
        hostname_ips = os.popen("hostname -I").read().strip()
        hostname = os.popen("hostname").read().strip()
        ip_addresses = hostname_ips.split()
        stack=""
        for ip in ip_addresses:
            if "." in ip:  
                stack+= ip+"\n"
        hostname_ip=stack
        hostname_unique_id = get_raspberry_pi_serial()
        
          
@app.route('/ipv4')
def get_local_ipv4():
    global hostname_ip
    refresh_hostname()
    return hostname_ip

@app.route('/ip')
def get_local_ips():
    global hostname_ips
    refresh_hostname()
    return hostname_ips

@app.route('/hostname')
def get_local_hostname():
    global  hostname
    refresh_hostname()
    return hostname

@app.route('/unique-id')
def get_unique_id():
    global hostname_unique_id
    refresh_hostname()
    return hostname_unique_id



bool_allows_anonymous_push = True
udp_local_listener_server = 3615
udp_local_listener_ip = "127.0.0.1"


string_url_params= "http://raspberrypi.local:8080/push_iid?index=INT&value=INT&date=ULONG&delayms=INT"
@app.route('/push_iid')
def push_integer():
    """
    Allows to push iid with http call if you need and trust your local network.
    http://raspberrypi.local:8080/push_iid?index=43&value=5&date=1634567890
    """
    if not bool_allows_anonymous_push:
        return "Pushing not allowed"
    
    index = request.args.get('index')
    value = request.args.get('value')
    date = request.args.get('date')
    delayms= request.args.get('delayms')
    if date is None and delayms is not None:
        date = int(time.time()*1000) + int(delayms)
    elif date is not None and delayms is not None:
        date = int(date) + int(delayms)
    elif date is not None and delayms is None:
        date = int(date)
    else:
        date = None
    
    
    bytes_to_send = None
    try:
        if index is not None and value is None and date is None:
            bytes_to_send = struct.pack('<i', int(index))
        elif index is not None and value is not None and date is None:
            bytes_to_send = struct.pack('<ii', int(index), int(value))
        elif index is None and value is not None and date is not None:
            bytes_to_send = struct.pack('<iQ', int(value), int(date))
        elif index is not None and value is not None and date is not None:
            bytes_to_send = struct.pack('<iiQ', int(index), int(value), int(date))
        
        if bytes_to_send is not None:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.sendto(bytes_to_send, (udp_local_listener_ip, udp_local_listener_server))
            udp_socket.close()
            return "Data pushed successfully"
        else:
            return "Invalid parameters. It should look like this: "+string_url_params
    except Exception as e:
        return f"Error: {e}"  
        
        
        
    


@app.route('/web3-min-js')
def web3_min_js():
    return render_template('www/asymmetric/web3.min.js')

@app.route('/reboot')
def reboot_page():
    if not bool_allows_to_reboot:
        return "Rebooting not allowed"
    else :  
        os.system("sudo reboot")
        return "Rebooting..."

@app.route('/ntp')
def ntp_page():
    return render_template('www/template/client_ntp_page.html')

@app.route('/ntp-offset', methods=['POST'])
def ntp_post_offset():
    dico ={}
    data = request.get_json()
    client_timestamp = data.get('timestamp')
    if client_timestamp is None:
        return jsonify({'error': 'Timestamp not provided'}), 400
    server_timestamp = int(time.time() * 1000)
    offset = server_timestamp - client_timestamp
    dico["offset"] = offset
    dico["server_timestamp"] = server_timestamp
    dico["client_timestamp"] = client_timestamp     
    return jsonify(dico)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
