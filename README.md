# API Categorizer

API Categorizer is a Flask-based web application that allows users to categorize APIs based on their response time and data size. Users can add APIs with curl commands, execute them to measure performance, and export the details to a PDF documentation.

## Features

- Add and delete APIs with curl commands.
- Execute curl commands and measure response time and data size.
- Automatically categorize APIs as Lightweight, Moderate, or Heavy.
- Export API details to a well-formatted PDF document.
- Include various sections in the documentation, such as Introduction, Authentication, Endpoints, Response Codes, Rate Limiting, Errors, Pagination, and Versioning.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/motiedivya/apiCategorizer.git
    cd apiCategorizer
    ```

2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Flask application:
    ```bash
    python app.py
    ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

3. Use the web interface to add APIs with their curl commands. Fill in the necessary details in the modal form and save the API.

4. Execute the APIs by clicking the `Execute` button. The application will measure the response time and data size, categorize the API, and save the response status and body.

5. Export the API details to a PDF by clicking the `Export` button. The PDF will include all the added APIs and their details, formatted in a well-structured document.

## API Fields

- **API Name**: The name of the API.
- **Curl Command**: The curl command to execute the API.
- **Method**: The HTTP method used in the curl command (e.g., GET, POST).
- **Endpoint**: The URL endpoint of the API.
- **Request Headers**: The headers included in the curl command.
- **Request Body**: The body of the request (for POST, PUT, etc.).
- **Response Status**: The status code of the API response.
- **Response Body**: The body of the API response.
- **Category**: The categorization of the API based on response time and data size (Lightweight, Moderate, Heavy).

## Project Structure

- `app.py`: The main Flask application file.
- `templates/index.html`: The HTML template for the web interface.
- `requirements.txt`: The list of required Python packages.
- `static/`: The directory for static files (CSS, JS, etc.).
- `README.md`: This README file.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or feedback, please feel free to contact us at [divyesh1099@gmail.com].

---

Enjoy using API Categorizer!
