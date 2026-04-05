# Khmer Data Annotation Tool

A web-based tool for annotating Khmer text datasets used in AI and machine learning projects.

---

## 📥 Getting Started

### Clone the Repository

```bash
git clone https://github.com/PunleuTY/Khmer-Data-Annotation-Project.git
cd Khmer-Data-Annotation-Project
cd production
```

### 📋 System Overview

This project consists of **4 components** that work together:

| Component | Port | Technology | Purpose |
|-----------|------|------------|---------|
| **MongoDB** | 27017 | Database | Data storage |
| **Backend** | 3000 | Go + Gin | API server |
| **ML Server** | 8000 | Python + FastAPI | OCR text extraction |
| **Frontend** | 5173 | React + Vite | Web interface |

### 🔧 Prerequisites

Install these before proceeding:

| Software | Version | Download |
|----------|---------|----------|
| **Node.js** | v18+ | https://nodejs.org/ |
| **Go** | v1.19+ | https://go.dev/dl/ |
| **Python** | v3.10+ | https://python.org/ |
| **MongoDB** | v6+ | https://mongodb.com/try/download/community |
| **Tesseract OCR** | v5+ | https://github.com/UB-Mannheim/tesseract/wiki |

### 📦 Installation

**1. Install Backend Dependencies:**
```bash
cd production/backend
go mod download
```

**2. Install Frontend Dependencies:**
```bash
cd production/frontend
npm install
```

**3. Install ML Dependencies:**
```bash
cd production/ML
pip install -r requirements.txt
```

### 🔐 Environment Configuration

**1. Backend (`backend/.env`):**
```bash
cd backend
copy .env.example .env
```

**2. Frontend (`frontend/.env`):**
```bash
cd frontend
copy .env.example .env
```

**3. ML Server (`ML/.env`):**
```bash
cd ML
copy .env.example .env
```

### ▶️ Running the Project

**Start in this order: MongoDB → Backend → ML → Frontend**

**Terminal 1: MongoDB**
```bash
net start MongoDB
# Or: mongod --dbpath "C:\data\db"
```

**Terminal 2: Backend Server**
```bash
cd production/backend
go run server.go
```

**Terminal 3: ML OCR Server**
```bash
cd production/ML/ML_V3_Final
python main_server.py
```

**Terminal 4: Frontend**
```bash
cd production/frontend
npm run dev
```

### ✅ Verify Everything is Running

| Service | URL | Expected Result |
|---------|-----|-----------------|
| Frontend | http://localhost:5173 | Web app loads |
| Backend API | http://localhost:3000 | 404 (normal) |
| ML API Docs | http://localhost:8000/docs | FastAPI Swagger UI |
| MongoDB | `mongo` in terminal | Connection successful |

---

## 🏗️ Project Structure

```
Khmer-Data-Annotation-Project/
├── production/     # Production-ready code
│   ├── backend/    # Go API server
│   │   ├── cloudflare/      # Cloudflare R2 storage
│   │   ├── controllers/     # Request handlers
│   │   ├── firebase/        # Firebase authentication
│   │   ├── middleware/      # Auth & request middleware
│   │   ├── models/          # Database schemas
│   │   ├── routes/          # API route definitions
│   │   └── server.go        # Main entry point
│   ├── frontend/   # React web interface
│   │   ├── src/
│   │   │   ├── components/  # Reusable UI components
│   │   │   ├── pages/       # Application pages
│   │   │   ├── contexts/    # React contexts
│   │   │   └── hooks/       # Custom hooks
│   └── ML/         # ML OCR services
│       └── ML_V3_Final/     # Production ML model
│           ├── utils/       # OCR utilities
│           └── main_server.py
└── experiment/     # Experimental features
```

---

## 🛠️ Tech Stack

| Component | Technology                       |
| --------- | -------------------------------- |
| Frontend  | React.js, Vite, Tailwind CSS     |
| Backend   | Go, Gin Framework                |
| Database  | MongoDB                          |
| ML/OCR    | Python, FastAPI, Tesseract, YOLO |

---

## 🔄 Component Workflow

```
┌─────────────┐
│   Frontend  │  (React - Port 5173)
│   User UI   │
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────┐
│   Backend   │  (Go - Port 3000)
│   API + DB  │──────► MongoDB (Port 27017)
└──────┬──────┘       (Store/Retrieve data)
       │
       │ OCR Requests
       ▼
┌─────────────┐
│  ML Server  │  (Python - Port 8000)
│  OCR + YOLO │──────► Tesseract (Khmer text)
└─────────────┘       (Extract text from images)
```

### Typical User Flow:

1. **User** opens frontend → Creates a project
2. **User** uploads an image → Backend stores it
3. **User** draws bounding boxes → Frontend sends coordinates
4. **Frontend** calls ML server → OCR extracts Khmer text
5. **ML Server** returns extracted text → Displayed in UI
6. **User** saves annotations → Backend stores in MongoDB

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `"No text extracted"` | Ensure ML server is running: `cd production/ML/ML_V3_Final && python main_server.py` |
| `"Cannot connect to backend"` | Start backend: `cd production/backend && go run server.go` |
| `"MongoDB connection failed"` | Run: `net start MongoDB` |
| `"TesseractNotFoundError"` | Install from https://github.com/UB-Mannheim/tesseract/wiki and add to PATH |
| `"Port already in use"` | Find process: `netstat -ano \| findstr :<PORT>` then `taskkill /PID <PID> /F` |
| `Firebase Authentication Errors` | Place `jomnam-service-account.json` in `backend/firebase/` |

**Quick Commands Reference:**
```bash
# Start all services
net start MongoDB
cd production/backend && go run server.go
cd production/ML/ML_V3_Final && python main_server.py
cd production/frontend && npm run dev

# Check ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

## 📖 Usage Demo

![GIF_demo](https://github.com/user-attachments/assets/f65da9dc-bc25-4c89-b215-3718e6a779be)

**Quick Workflow:**

1. Upload an image with Khmer text
2. Draw bounding boxes around text regions
3. Click "Extract Text" to run OCR
4. Review and edit extracted text
5. Save annotations to your project

---

## 👑 Honor Contributors

This project was made possible by the dedication and hard work of our core team:

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/PunleuTY">
        <img src="https://github.com/PunleuTY.png" width="100px;" alt="PunleuTY"/><br />
        <sub><b>PunleuTY</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Sitharath-s">
        <img src="https://github.com/Sitharath-s.png" width="100px;" alt="Sitharath-s"/><br />
        <sub><b>Sitharath-s</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/SeilaCP">
        <img src="https://github.com/SeilaCP.png" width="100px;" alt="SeilaCP"/><br />
        <sub><b>SeilaCP</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Leangchhay1523">
        <img src="https://github.com/Leangchhay1523.png" width="100px;" alt="Leangchhay1523"/><br />
        <sub><b>Leangchhay1523</b></sub>
      </a>
    </td>
  </tr>
</table>

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature`)
3. **Commit** your changes (`git commit -m "Add your feature"`)
4. **Push** to the branch (`git push origin feature/your-feature`)
5. **Open** a Pull Request

### Guidelines

- Keep commits clean and focused
- Write clear commit messages
- Test your changes before submitting

---

## 📄 License

This project is licensed under the MIT License.
