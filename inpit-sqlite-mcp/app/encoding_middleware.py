#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Middleware to handle URL encoding for non-ASCII characters in FastAPI
This middleware ensures proper handling of Japanese characters and spaces in URLs
"""

import re
from typing import Callable
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from urllib.parse import unquote


class URLEncodingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle URL encoding/decoding for non-ASCII characters in paths
    """
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process requests, decoding URL-encoded paths before passing to endpoint handlers
        """
        # Get the original URL path
        path = request.url.path
        
        # Check if we need to modify the path (paths with specific endpoints that need decoding)
        if any(pattern in path for pattern in ['/applicant/', '/application/', '/applicant-summary/', 
                                              '/visual-report/', '/assessment/', '/technical/',
                                              '/compare/', '/pdf-report/']):
            
            # Extract the endpoint name and parameter
            match = re.match(r'^(/.+?/)(.+)$', path)
            if match:
                endpoint_base = match.group(1)  # e.g. '/applicant/'
                param = match.group(2)          # e.g. '%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE'
                
                # Decode the parameter - ensure we decode any URL-encoded spaces
                decoded_param = unquote(param)
                
                # If there are raw spaces in the URL (which can happen in some client implementations),
                # they need to be preserved for proper routing
                if ' ' in decoded_param:
                    # Re-encode the spaces as %20 to maintain URL validity
                    # but keep the rest of the string as-is (already decoded)
                    decoded_param = decoded_param.replace(' ', '%20')
                
                # Create a new scope with modified path
                request.scope["path"] = f"{endpoint_base}{decoded_param}"
        
        # Process the request with the potentially modified path
        response = await call_next(request)
        return response
