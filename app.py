from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import time
import shlex
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

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
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("API Documentation", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Introduction", styles['Heading2']))
    story.append(Paragraph("The User Information API provides access to user data within our system. It allows developers to retrieve details about users registered in our platform.", styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Authentication", styles['Heading2']))
    story.append(Paragraph("This API requires API key authentication. Developers must include their API key in the request headers for authentication.", styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Endpoints", styles['Heading2']))

    for api in apis:
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"API Name: {api['name']}", styles['Heading3']))
        story.append(Paragraph(f"Curl Command: <code>{api['curl']}</code>", styles['BodyText']))
        story.append(Spacer(1, 6))
        
        data = [
            ["Method", "Endpoint", "Request Headers", "Request Body", "Response Status", "Response Body", "Category"],
            [api['method'], api['endpoint'], api['request_headers'], api['request_body'], api['response_status'], api['response_body'], api['category']]
        ]
        
        table = Table(data, colWidths=[60, 100, 100, 100, 60, 100, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Response Codes", styles['Heading2']))
    story.append(Paragraph("200 OK: Request successful, returns user data.", styles['BodyText']))
    story.append(Paragraph("201 Created: User created successfully.", styles['BodyText']))
    story.append(Paragraph("400 Bad Request: Invalid request format or missing parameters.", styles['BodyText']))
    story.append(Paragraph("401 Unauthorized: API key missing or invalid.", styles['BodyText']))
    story.append(Paragraph("404 Not Found: User not found.", styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Rate Limiting", styles['Heading2']))
    story.append(Paragraph("This API has a rate limit of 100 requests per hour per API key.", styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Errors", styles['Heading2']))
    story.append(Paragraph("400 Bad Request: Invalid request format. Check the request body and parameters.", styles['BodyText']))
    story.append(Paragraph("401 Unauthorized: Invalid API key. Make sure to include a valid API key in the request headers.", styles['BodyText']))
    story.append(Paragraph("404 Not Found: The requested user was not found.", styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Pagination", styles['Heading2']))
    story.append(Paragraph("Pagination is not supported in this version of the API.", styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Versioning", styles['Heading2']))
    story.append(Paragraph("This is version 1 of the User Information API. Future updates will be backward compatible.", styles['BodyText']))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="API_Documentation.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
