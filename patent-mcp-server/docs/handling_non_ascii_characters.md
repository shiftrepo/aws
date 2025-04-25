# Handling Non-ASCII Characters in Patent API URLs

## Problem

When making HTTP requests with non-ASCII characters (such as Japanese) in URL paths, you might encounter the error:

```
Invalid HTTP request received.
```

This happens because non-ASCII characters need to be properly URL-encoded before being included in a URL path.

## Solution

### 1. URL Encode Non-ASCII Characters

When using curl or any HTTP client to access endpoints with non-ASCII characters in the path (like Japanese applicant names), you must URL encode those characters.

For example, the Japanese company name "テック株式会社" should be encoded as `%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE`.

### 2. Use Our Helper Tools

We've provided two helper tools to assist with URL encoding:

#### A. Python URL Encoding Demo (`url_encode_demo.py`)

This Python script demonstrates how to properly URL encode Japanese applicant names and make API requests:

```bash
cd patent-mcp-server/app
python url_encode_demo.py
```

The script shows:
- Original applicant names
- Their URL-encoded equivalents
- How to construct proper API URLs
- Example API responses

#### B. Shell Script with curl Examples (`curl_examples.sh`)

This bash script provides ready-to-use curl commands with proper URL encoding:

```bash
cd patent-mcp-server/app
./curl_examples.sh
```

You can also generate a properly encoded curl command for any applicant name:

```bash
./curl_examples.sh "テック株式会社"
```

### 3. URL Encoding in Programming Languages

Here's how to properly URL encode in various programming languages:

#### Python
```python
import urllib.parse
encoded_name = urllib.parse.quote("テック株式会社")
url = f"http://localhost:8000/applicant/{encoded_name}"
```

#### JavaScript
```javascript
const encodedName = encodeURIComponent("テック株式会社");
const url = `http://localhost:8000/applicant/${encodedName}`;
```

#### Java
```java
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

String encodedName = URLEncoder.encode("テック株式会社", StandardCharsets.UTF_8.toString());
String url = "http://localhost:8000/applicant/" + encodedName;
```

#### Curl in Bash
```bash
applicant="テック株式会社"
encoded_applicant=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$applicant'))")
curl "http://localhost:8000/applicant/$encoded_applicant"
```

## Correct curl Example for "テック株式会社"

```bash
curl "http://localhost:8000/applicant/%E3%83%86%E3%83%83%E3%82%AF%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE"
```

Instead of:

```bash
# This will fail with "Invalid HTTP request received"
curl "http://localhost:8000/applicant/テック株式会社"
```

## API Documentation Update

The API documentation for endpoints that accept non-ASCII characters now includes specific instructions for proper URL encoding. See the updated FastAPI documentation at `http://localhost:8000/docs` for more details.
