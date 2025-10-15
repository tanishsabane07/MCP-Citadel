# MCP-Citadel 🛡️

## AI-Powered Security Vulnerability Analysis System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-19.1.1-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/flask-latest-green.svg)](https://flask.palletsprojects.com/)

MCP-Citadel is an intelligent security vulnerability analysis system that leverages Google's Gemini AI and machine learning to identify, classify, and provide remediation strategies for cybersecurity threats in real-time.

![MCP-Citadel Banner](https://via.placeholder.com/1200x300/4A90E2/FFFFFF?text=MCP-Citadel+Security+Scanner)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Dataset](#-dataset)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🤖 AI-Powered Analysis
- **Gemini AI Integration**: Leverages Google's latest Gemini 2.0 Flash model for intelligent threat analysis
- **Natural Language Processing**: Understands security queries in plain English
- **Context-Aware Classification**: Categorizes threats into 30+ vulnerability types

### 📊 Advanced Scoring System
- **CVSS Scoring**: Industry-standard vulnerability severity assessment (0-10 scale)
- **Hybrid Approach**: Combines heuristic keyword matching with ML-based semantic analysis
- **Multi-Dataset Correlation**: Compares queries against 200+ known vulnerability patterns

### 🎯 Comprehensive Analysis
- **Threat Classification**: SQL Injection, XSS, CSRF, Command Injection, and 30+ more
- **Severity Assessment**: Color-coded severity levels (Low, Medium, High, Critical)
- **Detailed Explanations**: 4-5 point analysis of why a vulnerability is concerning
- **Actionable Remediation**: 9-10 step-by-step security guidance

### 📈 History & Reporting
- **Query Logging**: Complete audit trail of all analyses
- **Historical Analysis**: Review past vulnerability assessments
- **CSV Export**: Download analysis history for reporting
- **Search & Filter**: Quick access to previous analyses

### 🎨 Modern User Interface
- **React Frontend**: Fast, responsive, and intuitive
- **Real-time Updates**: Instant feedback on analysis progress
- **Smooth Animations**: Framer Motion for seamless transitions
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  • User Interface Components                                 │
│  • Query Input & Results Display                             │
│  • History Viewer & Export                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API (HTTP/JSON)
┌──────────────────────▼──────────────────────────────────────┐
│                    BACKEND (Flask)                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  API Layer                                          │    │
│  │  /analyze | /history | /export_history            │    │
│  └─────────────┬──────────────────────────────────────┘    │
│                │                                             │
│  ┌─────────────▼───────────────────────────────────────┐   │
│  │  Business Logic Layer                               │   │
│  │  • Gemini AI Service (Classification)              │   │
│  │  • Scoring Service (CVSS Calculation)              │   │
│  │  • Search Service (Semantic Matching)              │   │
│  │  • History Database Service                        │   │
│  └─────────────┬───────────────────────────────────────┘   │
└────────────────┼──────────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────────┐
│                  DATA LAYER                                │
│  • SQLite: query_logs.db, scanner.db                      │
│  • JSON: attackbench.json (200+ vulnerabilities)          │
│  • External: Google Gemini API                            │
└───────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend
- **React** 19.1.1 - UI Framework
- **Axios** 1.12.2 - HTTP Client
- **Framer Motion** 12.23.24 - Animation Library
- **React Scripts** 5.0.1 - Build Tools

### Backend
- **Python** 3.8+ - Programming Language
- **Flask** - Web Framework
- **Flask-CORS** - Cross-Origin Support
- **SQLite3** - Database
- **scikit-learn** - Machine Learning
- **sentence-transformers** - Semantic Analysis

### AI & ML
- **Google Gemini AI** (gemini-2.0-flash-001) - LLM for analysis
- **TF-IDF Vectorization** - Feature extraction
- **Cosine Similarity** - Semantic matching
- **Sentence Transformers** - Text embeddings

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Google Gemini API key ([Get it here](https://ai.google.dev/))

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/tanishsabane07/MCP-Citadel.git
cd MCP-Citadel

# Navigate to backend
cd "Security Scanner (Backend)/backend"

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Initialize database and start server
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

```bash
# Navigate to frontend (from project root)
cd "security-scanner (Frontend)"

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will open automatically at `http://localhost:3000`

---

## 🚀 Usage

### Basic Workflow

1. **Start the Application**
   - Ensure both backend and frontend are running
   - Open `http://localhost:3000` in your browser

2. **Enter a Security Query**
   ```
   Example queries:
   - "SQL injection vulnerability in login form"
   - "JavaScript code executing in user profile"
   - "Exposed admin panel without authentication"
   - "Database credentials in configuration file"
   ```

3. **Analyze**
   - Click the "Analyze" button
   - Wait 2-5 seconds for AI processing

4. **Review Results**
   - **Classification**: Type of vulnerability (e.g., SQL Injection)
   - **Severity Score**: 0-10 rating with color indicator
   - **Explanation**: Detailed analysis in 4-5 points
   - **Remediation**: 9-10 actionable steps to fix
   - **Related Datasets**: Similar vulnerabilities from AttackBench

5. **View History**
   - Access past analyses
   - Export to CSV for reporting
   - Search and filter previous queries

### Example Analysis

**Query:** "Unvalidated user input in SQL query"

**Response:**
```json
{
  "classification": "sql-injection",
  "severity": 8.7,
  "explanation": "This vulnerability allows attackers to manipulate SQL queries...",
  "remediation": [
    "1. Use parameterized queries/prepared statements",
    "2. Implement input validation and sanitization",
    "3. Apply least privilege to database accounts",
    "4. Enable query logging and monitoring",
    "..."
  ],
  "datasets": [
    {
      "id": "AB-001",
      "title": "SQL Injection in login form",
      "similarity": 0.92
    }
  ]
}
```

---

## 📚 API Documentation

### POST /analyze

Analyzes a security query and returns comprehensive assessment.

**Endpoint:** `http://localhost:5000/analyze`

**Request:**
```json
{
  "query": "SQL injection in login form allowing authentication bypass",
  "example": {}
}
```

**Response:**
```json
{
  "classification": "sql-injection",
  "severity": 8.5,
  "explanation": "Detailed multi-point explanation...",
  "remediation": ["Step 1", "Step 2", ...],
  "debug": {
    "top_matches": [
      {
        "id": "AB-001",
        "title": "SQL Injection in login form",
        "similarity": 0.95,
        "description": "..."
      }
    ],
    "matched_keywords": ["sql", "injection", "login", "bypass"],
    "heuristic_score": 4.5,
    "semantic_score": 5.2
  },
  "datasets": [...]
}
```

**Response Codes:**
- `200 OK`: Successful analysis
- `400 Bad Request`: Invalid or missing query
- `500 Internal Server Error`: Server error

### GET /history

Retrieves analysis history.

**Endpoint:** `http://localhost:5000/history`

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:00",
      "query": "SQL injection in login",
      "classification": "sql-injection",
      "cvss_score": 8.5,
      "explanation": "...",
      "remediation": [...]
    }
  ]
}
```

### GET /export_history

Downloads analysis history as CSV.

**Endpoint:** `http://localhost:5000/export_history`

**Response:** CSV file download with columns:
- ID, Timestamp, Query, Classification, CVSS Score, Explanation, Remediation

---

## 📊 Dataset

### AttackBench Dataset

MCP-Citadel uses a curated dataset of 200+ security vulnerabilities:

**Statistics:**
- Total Vulnerabilities: 200+
- Unique Categories: 30+
- Impact Levels: 4 (Low, Medium, High, Critical)
- Real-world Examples: Yes

**Categories Include:**
- SQL Injection (Blind, Second-order, Error-based)
- Cross-Site Scripting (Reflected, Stored, DOM-based)
- Command Injection (OS, Template)
- Authentication & Authorization Issues
- Information Disclosure
- Insecure Deserialization
- SSRF, CSRF, IDOR
- Security Misconfigurations
- And 20+ more...

**Sample Entry:**
```json
{
  "id": "AB-001",
  "title": "SQL Injection in login form",
  "details": "Login endpoint concatenates user input into SQL queries and echoes DB errors.",
  "tag": "sql-injection",
  "impact": "high"
}
```

**Dataset Location:** `Security Scanner (Backend)/backend/data/attackbench.json`

---

## 📁 Project Structure

```
MCP-Citadel/
├── Security Scanner (Backend)/
│   └── backend/
│       ├── app.py                      # Main Flask application
│       ├── gemini_client.py            # Gemini API client
│       ├── dataset_service.py          # Dataset loader
│       ├── requirements.txt            # Python dependencies
│       ├── .env                        # Environment variables (create this)
│       ├── data/
│       │   ├── attackbench.json        # Vulnerability dataset
│       │   ├── query_logs.db           # Analysis history
│       │   └── scanner.db              # Application database
│       ├── services/
│       │   ├── gemini_service.py       # AI analysis service
│       │   ├── scoring.py              # CVSS scoring engine
│       │   ├── history_db.py           # Database operations
│       │   └── severity.py             # Severity calculation
│       ├── retriever/
│       │   └── search.py               # Semantic search
│       └── tools/
│           └── test_scoring.py         # Testing utilities
│
├── security-scanner (Frontend)/
│   ├── public/
│   │   ├── index.html
│   │   └── manifest.json
│   ├── src/
│   │   ├── App.js                      # Main React component
│   │   ├── QueryHistory.js             # History viewer component
│   │   ├── index.js                    # React entry point
│   │   └── App.css                     # Styles
│   ├── package.json                    # Node dependencies
│   └── README.md                       # Frontend documentation
│
├── SEMINAR_REPORT.md                   # Comprehensive seminar report
└── README.md                           # This file
```

---

## 🧪 Testing

### Backend Tests

```bash
cd "Security Scanner (Backend)/backend"

# Run scoring tests
python tools/test_scoring.py

# Test API endpoints with curl
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "SQL injection in login", "example": {}}'
```

### Frontend Tests

```bash
cd "security-scanner (Frontend)"

# Run test suite
npm test

# Run tests in watch mode
npm test -- --watch
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in `Security Scanner (Backend)/backend/`:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (defaults shown)
MODEL=gemini-2.0-flash-001
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
DB_PATH=data/query_logs.db
```

### Frontend Configuration

Update API endpoint in `src/App.js` if needed:

```javascript
const API_BASE_URL = 'http://localhost:5000';
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/MCP-Citadel.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

4. **Commit Your Changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**

### Contribution Guidelines

- Write clear commit messages
- Maintain code quality and consistency
- Update documentation for new features
- Add tests for bug fixes and new features
- Follow PEP 8 (Python) and Airbnb (JavaScript) style guides

---

## 🐛 Known Issues

- **Gemini API Latency**: Initial AI analysis may take 3-5 seconds
- **Dataset Size**: Currently limited to 200+ vulnerabilities
- **Browser Compatibility**: Best experience on Chrome/Firefox/Safari

---

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Real-time scanning integration
- [ ] Custom dataset upload
- [ ] Multi-language support
- [ ] PDF report generation
- [ ] Webhook notifications

### Version 3.0 (Future)
- [ ] SIEM integration
- [ ] CI/CD pipeline integration
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] Mobile application

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Contact & Support

**Developer:** Tanish Sabane  
**Email:** [Your Email]  
**GitHub:** [@tanishsabane07](https://github.com/tanishsabane07)

**Issues:** [GitHub Issues](https://github.com/tanishsabane07/MCP-Citadel/issues)  
**Documentation:** [Seminar Report](./SEMINAR_REPORT.md)

---

## 🙏 Acknowledgments

- **Google Gemini Team** - For providing access to Gemini AI API
- **OWASP Foundation** - For security best practices and guidelines
- **Open Source Community** - For amazing tools and libraries
- **FIRST.org** - For CVSS scoring standards

---

## 📖 Additional Resources

- [Seminar Report (Detailed)](./SEMINAR_REPORT.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CVSS Specification](https://www.first.org/cvss/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)

---

## 🌟 Star History

If you find this project useful, please consider giving it a star on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=tanishsabane07/MCP-Citadel&type=Date)](https://star-history.com/#tanishsabane07/MCP-Citadel&Date)

---

**Made with ❤️ for the Security Community**

