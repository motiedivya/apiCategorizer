from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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
    return total_time, data_size, response

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

@app.route('/')
def index():
    return render_template('index.html', apis=apis)

@app.route('/execute', methods=['POST'])
def execute():
    index = int(request.form['index'])
    curl_command = apis[index]['curl']
    total_time, data_size, response = execute_curl(curl_command)
    category = categorize_api(total_time, data_size)
    apis[index]['category'] = category
    return jsonify(index=index, category=category, time=total_time, size=data_size)

@app.route('/add_api', methods=['POST'])
def add_api():
    api_name = request.form['api_name']
    curl_command = request.form['curl_command']
    apis.append({'name': api_name, 'curl': curl_command, 'category': ''})
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

    pdf.drawString(30, 750, "API Documentation")
    pdf.drawString(30, 735, "------------------")

    y = 700
    for api in apis:
        pdf.drawString(30, y, f"API Name: {api['name']}")
        y -= 15
        pdf.drawString(30, y, f"Curl Command: {api['curl']}")
        y -= 15
        pdf.drawString(30, y, f"Category: {api['category']}")
        y -= 30

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="API_Documentation.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
