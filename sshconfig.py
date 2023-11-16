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

# Create the SSH session
session = pexpect.spawn('ssh ' + username + '@' + ip_address, encoding='utf-8', timeout=60)  # Increased timeout for SSH connection

# Define regular expressions for expected prompts
password_prompt = r'Password: '
enable_password_prompt = r'Password: '
prompt = re.compile(r'[>#]\s*$')

# Wait for the password prompt and enter the initial password
session.expect(password_prompt, timeout=20)  # Increased timeout for password prompt
session.sendline(password)

# Wait for the prompt (">" or "#") to ensure successful login
result = session.expect([prompt, pexpect.TIMEOUT, pexpect.EOF], timeout=20)  # Increased timeout for login

if result != 0:
    print('--- FAILURE! Login unsuccessful')
    exit()

# Enter enable mode
session.sendline('enable')
session.expect(enable_password_prompt, timeout=10)  # Increased timeout for enable password prompt
session.sendline(password_enable)

# Wait for the prompt in enable mode
result = session.expect(prompt, timeout=10)  # Increased timeout for enable prompt

if result != 0:
    print('--- FAILURE! Failed to enter enable mode')
    exit()

# Save the start-up configuration to a local file
session.sendline('show startup-config')
time.sleep(2)  # Added delay to ensure the command is executed before reading the output
session.expect(prompt)
with open(startup_config_file, 'w') as startup_file:
    startup_file.write(session.before)

# Enter configuration mode
session.sendline('configure terminal')
session.expect(r'\(config\)#', timeout=10)  # Increased timeout for config mode prompt

# Change the hostname to R1
session.sendline('hostname R1')
session.expect(r'R1\(config\)#', timeout=10)  # Increased timeout for hostname change prompt

# Save the running configuration to a local file
session.sendline('write memory')
time.sleep(2)  # Added delay to ensure the command is executed before reading the output
result = session.expect([prompt, pexpect.TIMEOUT, pexpect.EOF], timeout=10)  # Increased timeout for write memory
if result == 0:
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
