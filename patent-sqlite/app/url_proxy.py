#!/usr/bin/env python3

from flask import Flask, request, Response
import requests
import urllib.parse
import sys

app = Flask(__name__)

TARGET_HOST = "http://localhost:5000"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    # Log the incoming request
    print(f"Received request: {request.method} {request.full_path}", file=sys.stderr)
    
    # Build target URL with proper encoding
    target_url = f"{TARGET_HOST}/{path}"
    
    # Encode query parameters properly
    encoded_query_params = []
    for key, values in request.args.lists():
        for value in values:
            encoded_query_params.append(f"{key}={urllib.parse.quote_plus(value)}")
    
    if encoded_query_params:
        target_url += "?" + "&".join(encoded_query_params)
    
    print(f"Forwarding to: {target_url}", file=sys.stderr)
    
    # Forward the request to the target server
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        stream=True
    )
    
    # Print response status
    print(f"Got response: {resp.status_code}", file=sys.stderr)
    
    # Create response object
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    
    response = Response(resp.content, resp.status_code, headers)
    
    return response

if __name__ == '__main__':
    print("Starting URL proxy server on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
