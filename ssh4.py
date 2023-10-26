import pexpect
import re

# Define Variables
ip_address = "192.168.56.101"
username = "prne"
password = "cisco123!"
password_enable = "class123!"

# Create the SSH session
session = pexpect.spawn('ssh ' + username + '@' + ip_address, encoding='utf-8', timeout=20)

# Define regular expressions for expected prompts
password_prompt = r'Password: '
enable_password_prompt = r'Password: '
prompt = re.compile(r'[>#]\s*$')

# Wait for the password prompt and enter the initial password
session.expect(password_prompt)
session.sendline(password)

# Wait for the prompt (">" or "#") to ensure successful login
result = session.expect([prompt, pexpect.TIMEOUT, pexpect.EOF])

if result != 0:
    print('--- FAILURE! Login unsuccessful')
    exit()

# Enter enable mode
session.sendline('enable')
session.expect(enable_password_prompt)
session.sendline(password_enable)

# Wait for the prompt in enable mode
result = session.expect(prompt)

if result != 0:
    print('--- FAILURE! Failed to enter enable mode')
    exit()

# Enter configuration mode
session.sendline('configure terminal')
session.expect(r'\(config\)#')

# Change the hostname to Router 2
session.sendline('hostname Router 2')
session.expect(r'Router 2\(config\)#')

# Exit config mode
session.sendline('exit')

# Exit enable mode
session.sendline('exit')

# Display a success message if it works
print('-----------------------------------')
print('')
print('--- Success! Connecting to:', ip_address)
print('---   Username:', username)
print('')
print('------------------------------------')

# Terminate SSH session
session.close()
