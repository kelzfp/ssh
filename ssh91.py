import pexpect
import re
import difflib
import time

# Define Variables
ip_address = "192.168.56.101"
username = "prne"
password = "cisco123!"
password_enable = "class123!"
local_output_file = "output.txt"  # Local file to save the running configuration
startup_config_file = "startup_config.txt"  # Local file to save the startup configuration
comparison_file = "comparison.txt"  # Local file to save the comparison result

# Function to wait for command completion
def wait_for_prompt(session, prompt, timeout=10):
    try:
        session.expect(prompt, timeout=timeout)
        return True
    except pexpect.TIMEOUT:
        print(f"--- Timeout waiting for prompt: {prompt}")
        return False

# Create the SSH session
session = pexpect.spawn('ssh ' + username + '@' + ip_address, encoding='utf-8', timeout=60)  # Increased timeout for SSH connection

# Define regular expressions for expected prompts
password_prompt = r'Password: '
enable_password_prompt = r'Password: '
prompt = re.compile(r'[>#]\s*$')

# Wait for the password prompt and enter the initial password
if not wait_for_prompt(session, password_prompt):
    exit()

session.sendline(password)

# Wait for the prompt (">" or "#") to ensure successful login
if not wait_for_prompt(session, prompt):
    print('--- FAILURE! Login unsuccessful')
    exit()

# Enter enable mode
session.sendline('enable')

# Wait for the enable password prompt
if not wait_for_prompt(session, enable_password_prompt):
    print('--- FAILURE! Failed to enter enable mode')
    exit()

session.sendline(password_enable)

# Wait for the prompt in enable mode
if not wait_for_prompt(session, prompt):
    print('--- FAILURE! Failed to enter enable mode')
    exit()

# Save the start-up configuration to a local file
session.sendline('show startup-config')
if not wait_for_prompt(session, prompt):
    print('--- FAILURE! Unable to retrieve startup configuration')
    exit()

with open(startup_config_file, 'w') as startup_file:
    startup_file.write(session.before)

# Enter configuration mode
session.sendline('configure terminal')
if not wait_for_prompt(session, r'\(config\)#'):
    print('--- FAILURE! Failed to enter config mode')
    exit()

# Change the hostname to R1
session.sendline('hostname R1')
if not wait_for_prompt(session, r'R1\(config\)#'):
    print('--- FAILURE! Failed to change hostname to R1')
    exit()

# Save the running configuration to a local file
session.sendline('write memory')
if not wait_for_prompt(session, prompt):
    print('--- FAILURE! Unable to save running configuration')
    exit()

with open(local_output_file, 'w') as output_file:
    output_file.write(session.before)

# Exit config mode
session.sendline('exit')

# Exit enable mode
session.sendline('exit')

# Compare configurations
startup_config = open(startup_config_file).readlines()
local_config = open(local_output_file).readlines()

differ = difflib.Differ()
diff = list(differ.compare(startup_config, local_config))

# Save the comparison to a file
with open(comparison_file, 'w') as comparison_output:
    comparison_output.write('\n'.join(diff))

# Display a success message if it works
print('-----------------------------------')
print('')
print('--- Success! Connecting to:', ip_address)
print('---   Username:', username)
print('---   Password: ', password)
print('--- Output saved to:', local_output_file)
print('--- Startup configuration saved to:', startup_config_file)
print('--- Comparison saved to:', comparison_file)
print('')
print('------------------------------------')

# Terminate SSH session
session.close()
