# Leave Policy RAG Assistant

A Personalized Leave Policy Assistant built using Django, LangChain, FAISS, HuggingFace Embeddings, and Mistral AI.

The application allows employees to log in using their Employee ID and Password, view their leave information, and ask questions related to company leave policies through a Retrieval-Augmented Generation (RAG) chatbot.

---

## Features

### Authentication

* Employee Login
* Employee Signup
* Password-based Authentication
* Auto-fill employee information from Excel during signup

### Personalized RAG

* Employee-specific responses
* Employee ID aware
* Grade/Band aware
* PL / CL / SL taken information included in prompts

### Leave Policy Chatbot

* Ask leave policy questions
* LangChain RetrievalQA
* FAISS Vector Database
* Mistral LLM
* PDF-based knowledge retrieval

### Chat Features

* New Chat
* Clear Chat
* Chat History
* Open Previous Chats
* Delete Current Chat
* Sidebar Collapse / Expand

### Modern UI

* Responsive Design
* ChatGPT-style Chat Interface
* Suggested Questions
* Loading Animation
* Professional Sidebar

---

## Project Structure

```text
Leave_Policy_RAG/
│
├── data/
│   ├── leave.pdf
│   └── employees.xlsx
│
├── leave_app/
│   ├── templates/
│   │   └── leave_app/
│   │       ├── login.html
│   │       ├── signup.html
│   │       └── chat.html
│   │
│   ├── templatetags/
│   │   └── answer_filters.py
│   │
│   ├── views.py
│   ├── urls.py
│   └── models.py
│
├── static/
│   └── leave_app/
│       └── styles.css
│
├── auth_db.py
├── employee_data.py
├── loaders.py
├── splitter.py
├── embeddings_store.py
├── qa_chain.py
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## Tech Stack

### Backend

* Django 5
* Python 3.11

### AI / RAG

* LangChain
* FAISS
* HuggingFace Embeddings
* Mistral AI

### Data Sources

* PDF Leave Policy
* Excel Employee Database

### Frontend

* HTML
* CSS
* JavaScript

---

## Installation

### Clone Repository

```bash
git clone <your-repository-url>
cd Leave_Policy_RAG
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows:

```bash
.venv\Scripts\activate
```

Linux / Mac:

```bash
source .venv/bin/activate
```

### Install Requirements

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
MISTRAL_API_KEY=your_api_key_here
```

---

## Run Migrations

```bash
python manage.py migrate
```

---

## Start Application

```bash
python manage.py runserver
```

Application:

```text
http://127.0.0.1:8000
```

---

## Example Questions

### Leave Balance

```text
How many leaves are left?
```

### Sick Leave

```text
Can I take sick leave?
```

### Casual Leave

```text
Can I prefix CL with PL?
```

### Leave Encashment

```text
What is the PL encashment rule?
```

### Remaining Leave

```text
How many CL can I still take this year?
```

---

## Employee Data Format

Example Excel Structure:

| Employee ID | Name  | Grade | PL Taken | CL Taken | SL Taken |
| ----------- | ----- | ----- | -------- | -------- | -------- |
| E101        | Rahul | A     | 5        | 2        | 1        |
| E102        | Ashok | B     | 3        | 1        | 0        |

---

## Chat Features

### New Chat

Creates a fresh conversation and stores the current chat in history.

### Clear Chat

Deletes the currently opened chat.

### Chat History

Allows reopening previous conversations.

### Sidebar Toggle

Expand and collapse sidebar for a larger workspace.

---

## Future Enhancements

* Dark Mode
* Export Chat to PDF
* Voice Input
* Admin Dashboard
* Multi-PDF Support
* Advanced Analytics
* User Profile Management

---

## Author

Suryanandan Kumar

GitHub:
https://github.com/Suryanandankumar2003

---

## License

This project is intended for educational and learning purposes.
