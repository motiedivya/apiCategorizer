from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import time
import shlex
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Example data
apis = []

# Function to execute curl command and measure time and size
def execute_curl(curl_command):
    start_time = time.time()
    result = subprocess.run(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = time.time()
    total_time = end_time - start_time
    response = result.stdout.decode('utf-8')
    data_size = len(result.stdout)
    response_status = result.returncode
    return total_time, data_size, response_status, response

# Function to categorize API
def categorize_api(total_time, data_size):
    latency = 0.1  # Example latency, you might want to measure or adjust this
    processing_time = total_time - latency

    if processing_time < 0.05 and data_size < 100 * 1024:
        return "Lightweight"
    elif processing_time < 0.2 and data_size < 1 * 1024 * 1024:
        return "Moderate"
    else:
        return "Heavy"

# Function to parse curl command
def parse_curl_command(curl_command):
    args = shlex.split(curl_command)
    method = 'GET'
    endpoint = ''
    headers = {}
    data = ''
    
    for i, arg in enumerate(args):
        if arg == '-X' and i + 1 < len(args):
            method = args[i + 1]
        elif arg.startswith('http'):
            endpoint = arg
        elif arg == '-H' and i + 1 < len(args):
            header = args[i + 1].split(':', 1)
            if len(header) == 2:
                headers[header[0].strip()] = header[1].strip()
        elif arg == '--data' and i + 1 < len(args):
            data = args[i + 1]

    headers_str = '\n'.join([f"{k}: {v}" for k, v in headers.items()])
    return method, endpoint, headers_str, data

@app.route('/')
def index():
    return render_template('index.html', apis=apis)

@app.route('/execute', methods=['POST'])
def execute():
    index = int(request.form['index'])
    curl_command = apis[index]['curl']
    total_time, data_size, response_status, response = execute_curl(curl_command)
    category = categorize_api(total_time, data_size)
    apis[index]['category'] = category
    apis[index]['response_status'] = response_status
    apis[index]['response_body'] = response
    return jsonify(index=index, category=category, response_status=response_status, response_body=response)

@app.route('/add_api', methods=['POST'])
def add_api():
    api_name = request.form['api_name']
    curl_command = request.form['curl_command']
    method, endpoint, request_headers, request_body = parse_curl_command(curl_command)
    apis.append({
        'name': api_name,
        'curl': curl_command,
        'method': method,
        'endpoint': endpoint,
        'request_headers': request_headers,
        'request_body': request_body,
        'response_status': '',
        'response_body': '',
        'category': ''
    })
    return jsonify(apis=apis)

@app.route('/delete_api', methods=['POST'])
def delete_api():
    index = int(request.form['index'])
    apis.pop(index)
    return jsonify(apis=apis)

@app.route('/export', methods=['POST'])
def export():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("API Documentation")

    pdf.drawString(30, 750, "User Information API Documentation")
    pdf.drawString(30, 735, "Introduction")
    pdf.drawString(30, 720, "The User Information API provides access to user data within our system. It allows developers to retrieve details about users registered in our platform.")
    pdf.drawString(30, 705, "Authentication")
    pdf.drawString(30, 690, "This API requires API key authentication. Developers must include their API key in the request headers for authentication.")
    
    pdf.drawString(30, 675, "Endpoints")
    
    y = 660
    for api in apis:
        pdf.drawString(30, y, f"API Name: {api['name']}")
        y -= 15
        pdf.drawString(30, y, f"Curl Command: {api['curl']}")
        y -= 15
        pdf.drawString(30, y, f"Method: {api['method']}")
        y -= 15
        pdf.drawString(30, y, f"Endpoint: {api['endpoint']}")
        y -= 15
        pdf.drawString(30, y, f"Request Headers: {api['request_headers']}")
        y -= 15
        pdf.drawString(30, y, f"Request Body: {api['request_body']}")
        y -= 15
        pdf.drawString(30, y, f"Response Status: {api['response_status']}")
        y -= 15
        pdf.drawString(30, y, f"Response Body: {api['response_body']}")
        y -= 15
        pdf.drawString(30, y, f"Category: {api['category']}")
        y -= 30

    pdf.drawString(30, y, "Response Codes")
    y -= 15
    pdf.drawString(30, y, "200 OK: Request successful, returns user data.")
    y -= 15
    pdf.drawString(30, y, "201 Created: User created successfully.")
    y -= 15
    pdf.drawString(30, y, "400 Bad Request: Invalid request format or missing parameters.")
    y -= 15
    pdf.drawString(30, y, "401 Unauthorized: API key missing or invalid.")
    y -= 15
    pdf.drawString(30, y, "404 Not Found: User not found.")
    y -= 30

    pdf.drawString(30, y, "Rate Limiting")
    y -= 15
    pdf.drawString(30, y, "This API has a rate limit of 100 requests per hour per API key.")
    y -= 30

    pdf.drawString(30, y, "Errors")
    y -= 15
    pdf.drawString(30, y, "400 Bad Request: Invalid request format. Check the request body and parameters.")
    y -= 15
    pdf.drawString(30, y, "401 Unauthorized: Invalid API key. Make sure to include a valid API key in the request headers.")
    y -= 15
    pdf.drawString(30, y, "404 Not Found: The requested user was not found.")
    y -= 30

    pdf.drawString(30, y, "Pagination")
    y -= 15
    pdf.drawString(30, y, "Pagination is not supported in this version of the API.")
    y -= 30

    pdf.drawString(30, y, "Versioning")
    y -= 15
    pdf.drawString(30, y, "This is version 1 of the User Information API. Future updates will be backward compatible.")
    y -= 30

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="API_Documentation.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
