from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import time
import shlex
import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

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
        elif arg in ['--data', '--data-raw', '--data-binary'] and i + 1 < len(args):
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
    introduction = request.form['introduction']
    authentication = request.form['authentication']
    response_codes = json.loads(request.form['response_codes'])
    rate_limiting = request.form['rate_limiting']
    errors = request.form['errors']
    pagination = request.form['pagination']
    versioning = request.form['versioning']

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
        'category': '',
        'introduction': introduction,
        'authentication': authentication,
        'response_codes': response_codes,
        'rate_limiting': rate_limiting,
        'errors': errors,
        'pagination': pagination,
        'versioning': versioning
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
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    section_heading = ParagraphStyle(
        'section_heading',
        parent=styles['Heading2'],
        spaceAfter=12,
        spaceBefore=12,
    )
    story.append(Paragraph("API Documentation", styles['Title']))
    story.append(Spacer(1, 12))

    for api in apis:
        # API Title
        story.append(Paragraph(api['name'], styles['Heading1']))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.black, spaceBefore=1, spaceAfter=1))
        story.append(Spacer(1, 12))

        # Introduction Section
        story.append(Paragraph("Introduction", section_heading))
        story.append(Paragraph(api['introduction'], styles['BodyText']))
        story.append(Spacer(1, 12))

        # Authentication Section
        story.append(Paragraph("Authentication", section_heading))
        story.append(Paragraph(api['authentication'], styles['BodyText']))
        story.append(Spacer(1, 12))

        # Endpoint Section
        story.append(Paragraph("Endpoints", section_heading))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Curl Command: {api['curl']}", styles['BodyText']))
        story.append(Paragraph(f"Method: {api['method']}", styles['BodyText']))
        story.append(Paragraph(f"Endpoint: {api['endpoint']}", styles['BodyText']))
        story.append(Paragraph(f"Request Headers: {api['request_headers']}", styles['BodyText']))
        story.append(Paragraph(f"Request Body: {api['request_body']}", styles['BodyText']))
        story.append(Paragraph(f"Response Status: {api['response_status']}", styles['BodyText']))
        story.append(Paragraph(f"Response Body: {api['response_body']}", styles['BodyText']))
        story.append(Paragraph(f"Category: {api['category']}", styles['BodyText']))

        story.append(Spacer(1, 12))

        # Response Codes Section
        story.append(Paragraph("Response Codes", section_heading))
        for code in api['response_codes']:
            story.append(Paragraph(f"{code['statusCode']}: {code['description']}", styles['BodyText']))
        story.append(Spacer(1, 12))

        # Rate Limiting Section
        story.append(Paragraph("Rate Limiting", section_heading))
        story.append(Paragraph(api['rate_limiting'], styles['BodyText']))
        story.append(Spacer(1, 12))

        # Errors Section
        story.append(Paragraph("Errors", section_heading))
        story.append(Paragraph(api['errors'], styles['BodyText']))
        story.append(Spacer(1, 12))

        # Pagination Section
        story.append(Paragraph("Pagination", section_heading))
        story.append(Paragraph(api['pagination'], styles['BodyText']))
        story.append(Spacer(1, 12))

        # Versioning Section
        story.append(Paragraph("Versioning", section_heading))
        story.append(Paragraph(api['versioning'], styles['BodyText']))
        story.append(Spacer(1, 12))

        # Add a visual separator between APIs
        story.append(HRFlowable(width="100%", thickness=2, lineCap='round', color=colors.black, spaceBefore=1, spaceAfter=1))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="API_Documentation.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
