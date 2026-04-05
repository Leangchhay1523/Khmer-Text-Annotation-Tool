# Backend - Khmer Data Annotation Tool

A Go-based backend service for the Khmer Data Annotation Tool. This system handles image uploads, user authentication, project management, and coordinates with the ML OCR service for text extraction, with MongoDB storage.

## Features

- 🔐 **User Authentication**: Firebase-based authentication with email/password and Google sign-in
- 📁 **Project Management**: Create, update, and manage annotation projects
- 📤 **Image Upload**: Upload images with Cloudflare R2 storage integration
- 🤖 **ML Integration**: Coordinate with FastAPI ML service for OCR text extraction
- 📝 **Annotation Management**: Save and retrieve ground truth annotations
- 🗄️ **MongoDB Storage**: Persistent storage for users, projects, images, and annotations
- 📊 **Export Results**: Export annotation results in various formats

## Architecture

```
Frontend → Go Backend (Gin) → MongoDB
                      ↓
                  ML Server (FastAPI)
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Go + Gin |
| Database | MongoDB |
| Authentication | Firebase |
| Storage | Cloudflare R2 |
| OCR Service | FastAPI (Python) |

## Prerequisites

Before running this project, ensure you have the following installed:

- **Go** (version 1.19 or higher)
- **MongoDB** (version 6 or higher)
- **ML Server** (running on `http://localhost:8000`)

## Installation

### 1. Install Go Dependencies

```bash
cd backend
go mod download
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Configure the following variables:

```env
# Server
PORT=3000
GIN_MODE=debug

# MongoDB
MONGODB_URI=mongodb://localhost:27017
DB_NAME=annotation_db

# Firebase
FIREBASE_CREDENTIALS=firebase/jomnam-service-account.json

# Cloudflare R2 (optional)
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_ACCESS_KEY=your_access_key
CLOUDFLARE_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name

# CORS
FRONTEND_URL=http://localhost:5173
```

### 3. Set Up MongoDB

Make sure MongoDB is running on your system:

```bash
# Windows service
net start MongoDB

# Or manual
mongod --dbpath "C:\data\db"
```

### 4. Set Up Firebase Authentication

Place your Firebase service account JSON file in:

```
firebase/jomnam-service-account.json
```

This file is gitignored and must be obtained from your team.

### 5. Create Required Directories

```bash
mkdir -p uploads/temp uploads/final
```

## Running the Application

```bash
go run server.go
```

The server will start on `http://localhost:3000`

You should see:
```
✅ MongoDB connected successfully
[GIN-debug] Listening and serving HTTP on :3000
```

## API Endpoints

### Authentication Routes (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user with email/password |
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/google` | Login with Google OAuth |
| POST | `/api/auth/logout` | Logout current user |
| GET | `/api/auth/me` | Get current authenticated user info |

### User Routes (`/api/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/profile` | Get user profile |
| PUT | `/api/users/profile` | Update user profile |
| GET | `/api/users/recent` | Get user's recent annotations |

### Project Routes (`/api/projects`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects` | Create new project |
| GET | `/api/projects` | Get all projects for current user |
| GET | `/api/projects/:id` | Get specific project by ID |
| PUT | `/api/projects/:id` | Update project |
| DELETE | `/api/projects/:id` | Delete project |

### Image Upload Routes (`/api/upload`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload image for processing |
| GET | `/api/upload/:filename` | Get uploaded image |
| DELETE | `/api/upload/:filename` | Delete uploaded image |

### Result Routes (`/api/results`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/results/:projectId` | Get all results for a project |
| GET | `/api/results/:projectId/:imageId` | Get specific result |
| POST | `/api/results/save` | Save annotation result |
| PUT | `/api/results/:id` | Update annotation result |
| DELETE | `/api/results/:id` | Delete annotation result |

### Export Routes (`/api/export`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/export/:projectId` | Export project results |
| GET | `/api/export/:projectId/:format` | Download exported results |

## Project Structure

```
backend/
├── server.go                 # Application entry point
├── cloudflare/
│   └── r2.go                # Cloudflare R2 storage integration
├── controllers/
│   ├── authController.go    # Authentication logic
│   ├── projectController.go # Project management logic
│   ├── uploadController.go  # File upload logic
│   └── userController.go    # User management logic
├── firebase/
│   └── jomnam-service-account.json  # Gitignored credentials
├── middleware/
│   └── auth.go              # Authentication middleware
├── models/
│   ├── Image.go             # Image data model
│   └── User.go              # User data model
├── routes/
│   ├── authRoutes.go        # Auth route definitions
│   ├── projectRoutes.go     # Project route definitions
│   ├── resultRoutes.go      # Result route definitions
│   ├── uploadImageRoutes.go # Upload route definitions
│   └── userRoutes.go        # User route definitions
└── uploads/
    ├── temp/                # Temporary uploaded files
    └── final/               # Processed and verified files
```

## Data Models

### User Model

```go
type User struct {
    ID        primitive.ObjectID `bson:"_id,omitempty"`
    UID       string             `bson:"uid"`
    Email     string             `bson:"email"`
    Name      string             `bson:"name"`
    CreatedAt time.Time          `bson:"created_at"`
    UpdatedAt time.Time          `bson:"updated_at"`
}
```

### Image Model

```go
type Image struct {
    ID          primitive.ObjectID `bson:"_id,omitempty"`
    ProjectID   string             `bson:"project_id"`
    Name        string             `bson:"name"`
    Path        string             `bson:"path"`
    Width       int                `bson:"width,omitempty"`
    Height      int                `bson:"height,omitempty"`
    Status      string             `bson:"status"`
    Annotations []interface{}      `bson:"annotations"`
    Meta        Meta               `bson:"meta,omitempty"`
    CreatedAt   time.Time          `bson:"created_at"`
    UpdatedAt   time.Time          `bson:"updated_at"`
}
```

### Meta Model

```go
type Meta struct {
    Tool      string `bson:"tool,omitempty" json:"tool"`
    Lang      string `bson:"lang,omitempty" json:"lang"`
    Timestamp string `bson:"timestamp,omitempty" json:"timestamp"`
}
```

## Workflow

1. **Authentication**: User registers/logs in via Firebase
2. **Project Creation**: User creates a project to organize annotations
3. **Image Upload**: Client uploads image via `/api/upload`
4. **ML Processing**: Image is sent to FastAPI ML service for OCR
5. **Annotation**: User draws bounding boxes and reviews extracted text
6. **Save Results**: Verified annotations are saved to MongoDB
7. **Export**: User exports results in desired format

## Middleware

### Authentication Middleware

All protected routes use Firebase authentication middleware that:

- Validates Firebase ID tokens from request headers
- Extracts user information from the token
- Attaches user data to the request context
- Returns 401 Unauthorized for invalid/missing tokens

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful operation
- `201 Created`: Resource successfully created
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side errors

## Development

### Adding New Features

1. Create new controller functions in `controllers/`
2. Define routes in `routes/`
3. Update models in `models/` if needed
4. Register routes in `server.go`
5. Add middleware if authentication is required

### Testing

```bash
# Run tests (when available)
go test ./...

# Build the application
go build -o backend server.go

# Run the built binary
./backend
```

## Troubleshooting

### Common Issues

#### MongoDB Connection Failed
- Ensure MongoDB is running: `net start MongoDB`
- Check connection string in `.env` or `server.go`

#### Firebase Authentication Errors
- Verify `jomnam-service-account.json` exists in `firebase/` folder
- Check that the file has correct permissions
- Ensure Firebase project is properly configured

#### FastAPI Service Unavailable
- Verify ML server is running on `http://localhost:8000`
- Check network connectivity
- Test ML server at `http://localhost:8000/docs`

#### File Upload Errors
- Ensure `uploads/temp/` directory exists
- Check file permissions
- Verify Cloudflare R2 credentials if using cloud storage

#### Port Already in Use
- Find the process: `netstat -ano | findstr :3000`
- Kill the process: `taskkill /PID <PID> /F`
- Or change port in `.env`

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `PORT` | Yes | Server port (default: 3000) |
| `MONGODB_URI` | Yes | MongoDB connection string |
| `DB_NAME` | Yes | Database name |
| `FIREBASE_CREDENTIALS` | Yes | Path to service account JSON |
| `CLOUDFLARE_ACCOUNT_ID` | No | Cloudflare account ID for R2 |
| `CLOUDFLARE_ACCESS_KEY` | No | R2 access key |
| `CLOUDFLARE_SECRET_KEY` | No | R2 secret key |
| `R2_BUCKET_NAME` | No | R2 bucket name |
| `FRONTEND_URL` | Yes | Frontend URL for CORS |
| `GIN_MODE` | No | Gin framework mode (debug/release) |
