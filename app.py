from flask import Flask, request, render_template, redirect, url_for
import json
import paramiko
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import bcrypt
import os
import time
import re
import boto3
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
key = b'2QRt49fEUksjR6Yxpmjs98qtJ7-RYmKXLXblEKMuSjU='

ALLOWED_EXTENSIONS = {'dat', 'json'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', data_saved=False)

def create_ssh_client(server, port, user, password):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

def scp_transfer(file, remote_path, server, port, user, password):
    try:
        with create_ssh_client(server, port, user, password) as ssh_client:
            with SCPClient(ssh_client.get_transport()) as scp:
                scp.put(file, remote_path)
                # Optionally, log successful transfer
    except Exception as e:
        # Log any exceptions for debugging
        print(f"An error occurred during SCP transfer: {e}")
        logging.error(f"An error occurred: {e}")
        raise 

@app.route('/hpc-aws', methods=['POST'])
def handle_hpc_aws_login():
    username = request.form['username']
    password = request.form['password']
    aws_access_key_id = request.form['aws_access_key_id']
    aws_secret_access_key = request.form['aws_secret_access_key']
    print(generate_key())

    encrypted_password = encrypt_message(password, key)

    data = {'username': username, 'password': encrypted_password.decode('utf-8'), 'aws_access_key_id': aws_access_key_id, 'aws_secret_access_key': aws_secret_access_key}
        
    with open('data.json', 'w') as f:
        json.dump(data, f)
    
    return redirect(url_for('sw_upload'))

@app.route('/hpc-only', methods=['POST'])
def handle_hpc_login():
    username = request.form['username']
    password = request.form['password']
    
    print(generate_key())

    encrypted_password = encrypt_message(password, key)

    data = {'username': username, 'password': encrypted_password.decode('utf-8')}
        
    with open('data.json', 'w') as f:
        json.dump(data, f)
    
    return redirect(url_for('hpc_upload'))

@app.route('/sw_upload')
def sw_upload():
    return render_template('index.html', credentials_submitted=True)

@app.route('/hpc_upload')
def hpc_upload():
    return render_template('index.html', scp_files=True)

@app.route('/hpc_ready')
def hpc_ready():
    return render_template('index.html', files_uploaded=True)

@app.route('/upload_to_hpc1', methods=['POST'])
def upload_to_hpc1():
    json_file_path = 'data.json'
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_path = os.path.join('/tmp', filename)
            file.save(temp_path)


            server = 'gdtn.hpc.nyu.edu'
            port = 22
            with open(json_file_path, 'r') as file2:
                creds = json.load(file2)
            decrypted_password = decrypt_message(creds['password'].encode('utf-8'), key)
            user = creds['username']
            password = decrypted_password
            remote_path = '/scratch/ap7989/test/mro/cloudmrhubdata/'

            try:
                scp_transfer(temp_path, remote_path, server, port, user, password)
                os.remove(temp_path)
                return 'File uploaded to HPC successfully'
            except Exception as e:
                os.remove(temp_path)
                logging.error(f"An error occurred: {e}")
                return str(e)
        
@app.route('/upload_to_hpc2', methods=['POST'])
def upload_to_hpc2():
    json_file_path = 'data.json'
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_path = os.path.join('/tmp', filename)
            file.save(temp_path)


            server = 'gdtn.hpc.nyu.edu'
            port = 22
            with open(json_file_path, 'r') as file2:
                creds = json.load(file2)
            decrypted_password = decrypt_message(creds['password'].encode('utf-8'), key)
            user = creds['username']
            password = decrypted_password
            remote_path = '/scratch/ap7989/test/mro/cloudmrhubdata/'

            try:
                scp_transfer(temp_path, remote_path, server, port, user, password)
                os.remove(temp_path)
                return 'File uploaded to HPC successfully'
            except Exception as e:
                os.remove(temp_path)
                logging.error(f"An error occurred: {e}")
                return str(e)
        
@app.route('/upload_to_hpc3', methods=['POST'])
def upload_to_hpc3():
    json_file_path = 'data.json'
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_path = os.path.join('/tmp', filename)
            file.save(temp_path)


            server = 'gdtn.hpc.nyu.edu'
            port = 22
            with open(json_file_path, 'r') as file2:
                creds = json.load(file2)
            decrypted_password = decrypt_message(creds['password'].encode('utf-8'), key)
            user = creds['username']
            password = decrypted_password
            remote_path = '/scratch/ap7989/test/mro/mroptimum-jobs/'

            try:
                scp_transfer(temp_path, remote_path, server, port, user, password)
                os.remove(temp_path)
                return 'File uploaded to HPC successfully'
            except Exception as e:
                os.remove(temp_path)
                logging.error(f"An error occurred: {e}")
                return str(e)

@app.route('/upload_to_bucket1', methods=['POST'])
def upload_to_bucket1():
    with open('data.json', 'r') as file:
        creds = json.load(file)
    s3 = boto3.client('s3', aws_access_key_id=creds["aws_access_key_id"], aws_secret_access_key=creds["aws_secret_access_key"])
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        s3.upload_fileobj(file, "cloudmrhubdata", filename)
        return 'File uploaded to cloudmrhubdata successfully'

@app.route('/upload_to_bucket2', methods=['POST'])
def upload_to_bucket2():
    with open('data.json', 'r') as file:
        creds = json.load(file)
    s3 = boto3.client('s3', aws_access_key_id=creds["aws_access_key_id"], aws_secret_access_key=creds["aws_secret_access_key"])
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        s3.upload_fileobj(file, "cloudmrhubdata", filename)
        return 'File uploaded to cloudmrhubdata successfully'
    
@app.route('/upload_to_bucket3', methods=['POST'])
def upload_to_bucket3():
    with open('data.json', 'r') as file:
        creds = json.load(file)
    s3 = boto3.client('s3', aws_access_key_id=creds["aws_access_key_id"], aws_secret_access_key=creds["aws_secret_access_key"])
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        s3.upload_fileobj(file, "mroptimum-jobs", filename)
        return 'File uploaded to mroptimum-jobs successfully'
    
@app.route('/run_script', methods=['POST'])
def run_script():
    json_file_path = 'data.json'

    def ssh_connect(ssh_client, hostname, username, password):
        known_hosts_file = os.path.expanduser('~/.ssh/known_hosts')
        host_key_known = False
        try:
            with open(known_hosts_file, 'r') as file:
                for line in file:
                    if hostname in line:
                        host_key_known = True
                        break
        except FileNotFoundError:
            print(f"Known hosts file '{known_hosts_file}' not found. It will be created.")
            logging.error(f"An error occurred: {e}")

        if host_key_known:
            ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            print(f"Host key for {hostname} not known. Adding automatically.")
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(hostname, username=username, password=password)


    json_file_path = 'data.json'

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()

    try:
        with open(json_file_path, 'r') as file:
            creds = json.load(file)
        
        #Connecting to Gateway
        print("Connecting to gateway server...")
        decrypted_password = decrypt_message(creds['password'].encode('utf-8'), key)
        ssh_connect(ssh, 'gw.hpc.nyu.edu', creds['username'], decrypted_password)
        print("Connection to gateway successful \n")
        
        #Connecting to Greene
        print("Connecting to target server...")
        target_ssh = ssh.invoke_shell()

        target_ssh.send(f'ssh -q {creds["username"]}@greene.hpc.nyu.edu\n')
        # Wait for the password prompt and send the password
        # while not target_ssh.recv_ready():  # Wait for the server to be ready

        time.sleep(5)
        target_ssh.send(decrypted_password + '\n')
        print("Connection to target server successful\n")

        time.sleep(5)


        #Running sbatch file
        target_ssh.send('sbatch /scratch/'+creds["username"]+'/test/mro/run-mro.sbatch' + '\n')
        time.sleep(5)
        
        #Printing outputs
        output = target_ssh.recv(1024).decode('utf-8')
        pattern = r"Submitted batch job \d+"
        match = re.search(pattern, output)
        extracted_string="No Match Found"
        error_message="An error occured"
        if match:
            extracted_string = match.group()
        
        return render_template('index.html', script_output=extracted_string)

        
    
    except Exception as e:
        return render_template('index.html', error_message=e)
        logging.error(f"An error occurred: {e}")
    
    finally:
        ssh.close()

def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)