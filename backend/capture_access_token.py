from mitmproxy import http
import re
import sys
from datetime import datetime

# Set up logging to both console and file
log_file = open('mitmdump_output.log', 'a', buffering=1)

class TeeOutput:
    def __init__(self, *files):
        self.files = files
    
    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()
    
    def isatty(self):
        return self.files[0].isatty() if self.files else False
    
    def fileno(self):
        return self.files[0].fileno() if self.files else -1

# Redirect stdout and stderr to both console and file
sys.stdout = TeeOutput(sys.__stdout__, log_file)
sys.stderr = TeeOutput(sys.__stderr__, log_file)

# Log session start
print(f"\n{'='*60}")
print(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}\n")

# Regular expression to match the access token in the Authorization header
token_pattern = re.compile(r'Bearer (\S+)')

def request(flow: http.HTTPFlow) -> None:
    # Check if the request is to Uber's API
    if 'uber.com' in flow.request.pretty_url and '/api/' in flow.request.pretty_url:
        # Print the request details for debugging
        print(f"\n{'='*60}")
        print(f"Intercepted API request: {flow.request.pretty_url}")
        print(f"Method: {flow.request.method}")
        
        # Print all headers
        if flow.request.headers:
            print(f"\nRequest Headers:")
            for name, value in flow.request.headers.items():
                if name.lower() in ['authorization', 'cookie', 'x-csrf-token', 'x-api-key']:
                    print(f"  {name}: {value}")
        
        # Save cookies to file
        if 'Cookie' in flow.request.headers:
            cookies = flow.request.headers['Cookie']
            print(f"\n*** SAVING COOKIES ***")
            with open('uber_cookies.txt', 'w') as f:
                f.write(cookies)
            print(f"Cookies saved to uber_cookies.txt")
        
        # Check if the Authorization header is present
        if 'Authorization' in flow.request.headers:
            # Extract the access token using the regular expression
            match = token_pattern.search(flow.request.headers['Authorization'])
            if match:
                access_token = match.group(1)
                print(f"\n*** CAPTURED ACCESS TOKEN: {access_token} ***")
                # Save the token to a file
                with open('uber_access_token.txt', 'w') as f:
                    f.write(access_token)
        print(f"{'='*60}\n")

def response(flow: http.HTTPFlow) -> None:
    # Check if the response is from Uber's API
    if 'uber.com' in flow.request.pretty_url:
        # Check for tokens in response body (for OAuth flows)
        if flow.response and flow.response.content:
            try:
                content = flow.response.content.decode('utf-8', errors='ignore')
                # Look for common token patterns in response
                if any(keyword in content.lower() for keyword in ['access_token', 'accesstoken', 'bearer', 'jwt']):
                    print(f"\n*** POTENTIAL TOKEN IN RESPONSE ***")
                    print(f"URL: {flow.request.pretty_url}")
                    print(f"Response Status: {flow.response.status_code}")
                    # Try to find JSON with access_token
                    if 'access_token' in content:
                        import json
                        try:
                            data = json.loads(content)
                            if 'access_token' in data:
                                token = data['access_token']
                                print(f"*** CAPTURED ACCESS TOKEN FROM RESPONSE: {token} ***")
                                with open('uber_access_token.txt', 'w') as f:
                                    f.write(token)
                        except:
                            pass
                    print(f"***\n")
            except:
                pass
        
        # Check Set-Cookie headers
        if flow.response and 'Set-Cookie' in flow.response.headers:
            cookies = flow.response.headers.get_all('Set-Cookie')
            for cookie in cookies:
                if any(keyword in cookie.lower() for keyword in ['token', 'auth', 'session', 'jwt']):
                    print(f"\n*** AUTH COOKIE SET ***")
                    print(f"URL: {flow.request.pretty_url}")
                    print(f"Cookie: {cookie[:100]}...")
                    print(f"***\n")

# Run mitmproxy with the script
if __name__ == "__main__":
    from mitmproxy.tools.main import mitmdump
    try:
        mitmdump(['-s', __file__, '--mode', 'regular', '-p', '8080'])
    finally:
        # Log session end and close file
        print(f"\n{'='*60}")
        print(f"Session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        log_file.close()