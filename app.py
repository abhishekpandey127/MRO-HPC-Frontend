from flask import Flask, request, render_template, redirect, url_for
import json
import paramiko
import json
import os
import time
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', data_saved=False)

@app.route('/submit-form', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']  # In a real app, hash the password

    data = {'username': username, 'password': password}
    
    with open('data.json', 'w') as f:
        json.dump(data, f)
    
    # Redirect to the same page but with data_saved set to True
    return redirect(url_for('run_script_page'))

@app.route('/run-script-page')
def run_script_page():
    return render_template('index.html', credentials_submitted=True)

@app.route('/run_script', methods=['POST'])
def run_script():
    json_file_path = 'data.json'

    # Function to connect to an SSH server
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
        ssh_connect(ssh, 'gw.hpc.nyu.edu', creds['username'], creds['password'])
        print("Connection to gateway successful \n")
        
        #Connecting to Greene
        print("Connecting to target server...")
        target_ssh = ssh.invoke_shell()

        target_ssh.send(f'ssh -q {creds["username"]}@greene.hpc.nyu.edu\n')
        # Wait for the password prompt and send the password
        # while not target_ssh.recv_ready():  # Wait for the server to be ready

        time.sleep(5)
        target_ssh.send(creds['password'] + '\n')
        print("Connection to target server successful\n")

        time.sleep(5)


        #Running sbatch file
        #print("Submitting batch job")
        #target_ssh.send('ls /scratch/'+creds["username"]+'/test/mro/' + '\n')
        target_ssh.send('sbatch /scratch/'+creds["username"]+'/test/mro/run-mro.sbatch' + '\n')
        time.sleep(5)
        
        #Printing outputs
        output = target_ssh.recv(1024).decode('utf-8')
        pattern = r"Submitted batch job \d+"
        match = re.search(pattern, output)
        extracted_string="No Match Found"
        if match:
            extracted_string = match.group()
        return f"<h1>Script Output</h1><p>{extracted_string}</p>"

    except Exception as e:
        # Handle exceptions and return an error message
        return f"<h1>Error</h1><p>{e}</p>"
    except FileNotFoundError:
        print(f"Credentials file '{json_file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file '{json_file_path}'.")
    except KeyError:
        print(f"Missing required credential fields in '{json_file_path}'.")
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials")
    except paramiko.BadHostKeyException as badHostKeyException:
        print("Unable to verify server's host key: %s" % badHostKeyException)
    except paramiko.SSHException as e:
        print("SSH error: ", e)
    except Exception as e:
        print("Operation error: %s" % e)
    finally:
        ssh.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)