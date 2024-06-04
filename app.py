from flask import Flask, render_template, request, jsonify
import subprocess
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Example data
apis = []

# Function to execute curl command and measure time
def execute_curl(curl_command):
    start_time = time.time()
    result = subprocess.run(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = time.time()
    total_time = end_time - start_time
    response = result.stdout.decode('utf-8')
    return total_time, response

# Function to categorize API
def categorize_api(total_time):
    latency = 0.1  # Example latency, you might want to measure or adjust this
    processing_time = total_time - latency

    if processing_time < 0.05:
        return "Lightweight"
    elif processing_time < 0.2:
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
    total_time, response = execute_curl(curl_command)
    category = categorize_api(total_time)
    apis[index]['category'] = category
    return jsonify(index=index, category=category, time=total_time)

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

if __name__ == '__main__':
    app.run(debug=True)
