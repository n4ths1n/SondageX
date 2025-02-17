# **Survey Project Documentation**  

## **Introduction**  

This project is a web-based survey application designed to allow users to answer questionnaires and administrators to dynamically manage questions and visualize responses in different graphical formats (bar chart, pie chart, sociogram). The application is built with **Python** and **Flask**, uses **SQLAlchemy** for database management, and **Flask-Login** for administrator authentication. The interface is developed with **Bootstrap** (for a responsive experience) and **Font Awesome** (for icons).  

---

## **Project Structure**  

The project is organized as follows:  

```
project/
├── application.py         # Main Flask application file
├── models.py              # Data models definition (Question, Response)
├── README.md              # Complete documentation (this file)
└── templates/             # Folder containing all HTML files
    ├── base.html          # Base template (includes links to Bootstrap, Font Awesome, favicon, etc.)
    ├── survey.html        # Survey form accessible to users (wizard mode)
    ├── login.html         # Administrator login form
    ├── admin.html         # Admin dashboard (manage questions, responses, and visualizations)
    ├── add_question.html  # Form to add a question
    ├── edit_question.html # Form to edit an existing question
    ├── graph.html         # Page displaying a chart (bar or pie)
    ├── sociogram.html     # Page displaying a question's sociogram
    └── view_response.html # Page displaying detailed response information
└── static/                # Folder for static files
    ├── logo.ico    # Favicon
    └── logo.jpg    # Company logo
```

---

## **Prerequisites**  

- **Python 3.x** installed on your machine.  
- The following Python modules must be installed:  

```bash
pip install flask flask_sqlalchemy flask_login matplotlib networkx pandas
```

---

## **Installation and Configuration**  

1. **Clone the project** into your working directory.  

2. **Create a virtual environment** (optional but recommended):  

   - On Windows:  
     ```batch
     python -m venv env
     env\Scripts\activate
     ```
   - On Linux/Mac:  
     ```bash
     python3 -m venv env
     source env/bin/activate
     ```

3. **Install dependencies** (if not already installed):  
   ```bash
   pip install flask flask_sqlalchemy flask_login matplotlib networkx pandas
   ```

4. **Place static files**:  
   - Copy `logo.ico` into the `static/` folder (this will be your favicon).  
   - Copy `logo.jpg` into the `static/` folder (this will be the company logo).  

5. **Run the application**:  

   From the project root, execute:  
   ```bash
   python application.py
   ```
   The application will be accessible at [http://X.X.X.X:5000](http://X.X.X.X:5000).  

6. **Access the admin interface**:  

   Go to [http://X.X.X.X:5000/login](http://X.X.X.X:5000/login)  
   (Username: **admin**, Password: **admin**).  

---

## **Key Files Description**  

### 1. `application.py`  

- **Flask and SQLAlchemy Configuration**:  
  Initializes the application with an SQLite database and defines the secret key.  

- **Authentication Management**:  
  Uses **Flask-Login** to manage the administrator (predefined account `admin`/`admin`).  

- **Main Routes**:  
  - `/` : Displays the survey form accessible to all users.  
  - `/login` and `/logout` : Handle administrator login/logout.  
  - `/admin` : Admin dashboard for managing questions and viewing responses.  
  - Routes to add, edit, and delete questions.  
  - Routes to display visualizations (bar chart, pie chart, sociogram) for each question.  
  - Route to display an individual response (`/response/<int:response_id>`).  

- **Note on `@app.before_request`**:  
  The function decorated with `@app.before_request` is used to create tables and insert default data if no questions exist.  

### 2. `models.py`  

- **Model `Question`**:  
  - `title` : The question text.  
  - `question_type` : The expected response type (e.g., `multiple`, `dropdown`, `dropdown9`, `text`, `numeric`, `date`).  
  - `options` : Response options stored in JSON format (used for types like `multiple` or `dropdown`).  

- **Model `Response`**:  
  - `name` : Respondent's name.  
  - `department` : Respondent's department.  
  - `answers` : Answers provided by the respondent (stored as JSON).  
  - `timestamp` : Date and time of the response.  

### 3. HTML Templates  

- **`base.html`**:  
  The base template includes:  
  - A meta viewport tag for responsive design.  
  - Links to Bootstrap and Font Awesome.  
  - The favicon (`logo.ico`).  
  - A basic structure to display flash messages and content from other templates.  

- **`survey.html`**:  
  The user survey form in "wizard" mode (multi-step):  
  - Step 0: Personal information (Name, Surname, and Department via a dropdown).  
  - Following steps: One step per question. The displayed input type depends on `question_type` (checkbox, dropdown, text, numeric, date, etc.).  
  - Final step: Thank you message and a "Close Window" button centered on the page.  

- **`login.html`**:  
  Administrator login form.  

- **`admin.html`**:  
  The administrator dashboard allowing:  
  - Managing questions (add, edit, delete).  
  - Viewing response visualizations (bar chart, pie chart, sociogram).  
  - Viewing the list of responses and accessing detailed responses.  
  - Deleting all responses with a dedicated button.  

- **`add_question.html` and `edit_question.html`**:  
  Forms for creating or editing a question. The administrator can select `question_type` from several options (`multiple`, `dropdown`, `dropdown9`, `text`, `numeric`, `date`) and enter response options if applicable.  

- **`graph.html`**:  
  Displays a generated chart (bar or pie) for a given question.  

- **`sociogram.html`**:  
  Displays the sociogram for a given question (graphical representation of relationships between respondents and response options).  

- **`view_response.html`**:  
  Displays detailed user response data.  

---

## **Graphical Visualizations**  

For each question, three visualization options are available in the admin panel:  

- **Bar Chart** : Displays the number of responses per option.  
- **Pie Chart** : Shows the percentage distribution of responses.  
- **Sociogram** : Graphically represents relationships between respondents and response options (uses NetworkX).  

These visualizations are generated dynamically and displayed on dedicated pages.  

---

## **Security and Authentication**  

Authentication is managed via **Flask-Login**. Only the administrator (predefined account) can access admin pages and manage questions/responses.  

---

## **Deployment**  

For production deployment, it is recommended to use a WSGI server (such as **Gunicorn** or **uWSGI**) and configure a reverse proxy (with **Nginx** or **Apache**) to handle requests and the domain (you can replace the IP with a domain name).  

---

## **Conclusion**  

This project provides a complete solution for conducting and managing online surveys. It includes:  

- A modern, responsive user survey form.  
- A full-featured admin dashboard with dynamic question management and graphical visualizations.  
- Various response types and detailed visual representations.  

We hope this detailed documentation helps you understand, deploy, and customize the project according to your needs. 🚀
