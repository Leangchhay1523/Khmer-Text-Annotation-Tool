# Frontend - Khmer Data Annotation Tool

## Overview

This is the frontend component of the Khmer Data Annotation Tool, built with **React 19** and **Vite** for fast development and optimal performance. The application provides a modern, responsive user interface for data annotation workflows.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | React 19 |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| State Management | React Context |
| Authentication | Firebase |
| Routing | React Router |
| UI Components | Custom components + shadcn/ui |

## 🚀 Quick Start

### Install Dependencies

```bash
cd frontend
npm install
```

### Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Set Up Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Configure the following variables:

```env
# API Endpoints
VITE_BACKEND_URL=http://localhost:3000
VITE_ML_SERVER_URL=http://localhost:8000

# Firebase (if using client-side auth)
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
VITE_FIREBASE_PROJECT_ID=your_project_id

# App Configuration
VITE_APP_NAME=Khmer Annotation Tool
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # shadcn/ui components
│   │   │   └── Profile/   # Profile-specific components
│   │   ├── AdvisorCard.jsx
│   │   ├── annotation-canvas.jsx
│   │   ├── annotation-list.jsx
│   │   ├── Card.jsx
│   │   ├── CreateProjectDialog.jsx
│   │   ├── CreateProjectForm.jsx
│   │   ├── export-dialog.jsx
│   │   ├── Footer.jsx
│   │   ├── GalleryView.jsx
│   │   ├── I18nProvider.jsx
│   │   ├── image-uploader.jsx
│   │   ├── ImageUploader.jsx
│   │   ├── json-editor.jsx
│   │   ├── Keyboard_Shortcuts.jsx
│   │   ├── MemberCard.jsx
│   │   ├── MissionVision.jsx
│   │   ├── ocr-controls.jsx
│   │   ├── ProtectedRoute.jsx
│   │   └── translator-provider.jsx
│   ├── contexts/
│   │   └── AuthContext.jsx       # Authentication context
│   ├── hooks/
│   │   └── useAuth.js            # Authentication hook
│   ├── lib/
│   │   ├── auth/                 # Authentication utilities
│   │   │   ├── emailPassAuth.js
│   │   │   ├── firebase.js
│   │   │   ├── googleAuth.js
│   │   │   └── index.js
│   │   ├── api.js                # API client functions
│   │   ├── authUtils.js
│   │   ├── dataUtils.js
│   │   ├── download.js
│   │   ├── exporters.js
│   │   ├── i18n-dictionaries.js
│   │   ├── levenshtein.js
│   │   ├── storage.js
│   │   ├── transtator-dictionaries.js
│   │   ├── userShortcuts.js
│   │   └── utils.js
│   ├── navigations/
│   │   ├── Layout.jsx            # Main layout component
│   │   └── navigate.jsx          # Navigation logic
│   ├── pages/
│   │   ├── About.jsx             # About page
│   │   ├── Annotate.jsx          # Main annotation interface
│   │   ├── Feature.jsx           # Features page
│   │   ├── Home.jsx              # Landing page
│   │   ├── Login.jsx             # Login page
│   │   ├── Myproject.jsx         # User's projects page
│   │   ├── Signup.jsx            # Registration page
│   │   └── Userprofile.jsx       # User profile page
│   ├── server/
│   │   ├── deleteAPI.js          # Delete API functions
│   │   ├── exportResultAPI.js    # Export API functions
│   │   ├── getProjectResult.js   # Get project results
│   │   ├── saveResultAPI.js      # Save results API
│   │   └── sendImageAPI.js       # Image upload API
│   ├── types/
│   │   ├── dataFormat.js
│   │   ├── frontendUnifiedSchema.js
│   │   ├── frontendUnifiedSchema.json
│   │   ├── simpleSchema.js
│   │   └── standardSchema.js
│   ├── assets/
│   │   ├── fonts/
│   │   │   └── CADTMonoDisplay-Regular.ttf  # Custom Khmer font
│   │   ├── profiles/            # Team member profile photos
│   │   ├── homepage1.jpg
│   │   ├── JomNam_New_Logo1.png
│   │   └── Nav2.png
│   ├── App.jsx                   # Main application component
│   ├── App.css                   # App-specific styles
│   ├── main.jsx                  # Application entry point
│   └── index.css                 # Global styles with Tailwind
├── .env                          # Environment variables
├── .gitignore
├── components.json               # shadcn/ui configuration
├── eslint.config.js
├── index.html
├── jsconfig.json
├── package.json
├── postcss.config.js
├── tailwind.config.js
└── vite.config.js
```

## Key Components

### Annotation Interface (`pages/Annotate.jsx`)

The main annotation page provides:

- **Image Upload**: Drag-and-drop or file selection
- **Canvas Drawing**: Draw bounding boxes around text regions
- **OCR Extraction**: Call ML server to extract text from boxes
- **Text Editing**: Review and edit extracted text
- **Save/Export**: Save annotations to project or export results

### Authentication System

- **Firebase Integration**: Email/password and Google OAuth
- **Protected Routes**: Authentication required for annotation features
- **User Context**: Global auth state management via `AuthContext`
- **Session Management**: Persistent login with Firebase tokens

### API Integration

Server communication through:

- `src/server/` - API client functions for backend endpoints
- `VITE_BACKEND_URL` - Backend API base URL
- `VITE_ML_SERVER_URL` - ML OCR service base URL

### Internationalization (i18n)

- **Language Support**: Khmer and English
- **Translation Provider**: `translator-provider.jsx` component
- **Dictionaries**: `i18n-dictionaries.js` and `transtator-dictionaries.js`

## Available Scripts

```bash
# Development
npm run dev              # Start dev server with hot reload

# Production
npm run build            # Build for production
npm run preview          # Preview production build

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint issues automatically
```

## Component Architecture

### Reusable Components (`components/`)

Components that can be used across multiple pages:

- **UI Elements**: Button, Card, Dialog, Input, etc.
- **Annotation Tools**: Canvas, annotation list, OCR controls
- **Project Management**: Create project dialog/form
- **Export Tools**: Export dialog for various formats

### Page Components (`pages/`)

Complete page views representing different routes:

- **Home.jsx** - Landing page with features overview
- **Annotate.jsx** - Main annotation interface
- **Myproject.jsx** - User's project dashboard
- **Userprofile.jsx** - User profile and settings
- **About.jsx** - About page with team info
- **Feature.jsx** - Features showcase
- **Login.jsx / Signup.jsx** - Authentication pages

### Context & Hooks

- **AuthContext.jsx** - Global authentication state and methods
- **useAuth.js** - Custom hook for accessing auth context

## Styling

### Tailwind CSS Configuration

- **Framework**: Tailwind CSS v4 with Vite plugin
- **Custom Font**: CADTMonoDisplay for Khmer text
- **Theme Variables**: Defined in `index.css`
- **Responsive Design**: Mobile-first approach

### Custom Font

The project uses a custom Khmer font:

```css
@font-face {
  font-family: 'CADTMonoDisplay-Regular';
  src: url('./assets/fonts/CADTMonoDisplay-Regular.ttf') format('truetype');
}
```

## State Management

### React Context

- **AuthContext**: User authentication state
- **Provider Pattern**: I18n and translation state

### Local State

- Component-level state with `useState` and `useReducer`
- Custom hooks for reusable logic

## Routing

The application uses React Router for navigation:

```jsx
<BrowserRouter>
  <Layout>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
      <Route path="/features" element={<Feature />} />
      <Route path="/annotate" element={<ProtectedRoute><Annotate /></ProtectedRoute>} />
      <Route path="/my-projects" element={<ProtectedRoute><Myproject /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Userprofile /></ProtectedRoute>} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
    </Routes>
  </Layout>
</BrowserRouter>
```

## Data Flow

```
User Action
    ↓
React Component
    ↓
API Call (src/server/)
    ↓
Backend API (Go)
    ↓
MongoDB / ML Server
    ↓
Response
    ↓
Update UI
```

## Development Guidelines

### Adding New Components

1. **Determine type**: Is it reusable (components/) or page-specific (pages/)?
2. **Follow naming**: PascalCase for components, camelCase for utilities
3. **Use Tailwind**: Style with Tailwind CSS classes
4. **Add to navigation**: Register new routes in navigation components

### Code Style

- **Imports**: Group imports (React, libraries, local)
- **Exports**: Use named exports, default export for pages
- **PropTypes**: Document component props
- **Error Handling**: Handle API errors gracefully with user feedback

### Best Practices

1. **Component Reusability**: Extract common patterns into components
2. **Lazy Loading**: Use React.lazy for code splitting on large pages
3. **Error Boundaries**: Wrap components with error boundaries
4. **Accessibility**: Use semantic HTML and ARIA attributes
5. **Performance**: Memoize expensive calculations with useMemo/useCallback

## Build & Deployment

### Development

```bash
npm run dev
```

- Hot module replacement (HMR)
- Source maps enabled
- Development server on port 5173

### Production Build

```bash
npm run build
```

- Minified and optimized bundles
- Assets in `dist/` directory
- Ready for static hosting

### Preview Production Build

```bash
npm run preview
```

- Serves the production build locally
- Test optimized assets before deployment

## Troubleshooting

### Common Issues

#### Dependencies Not Installing
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Port Already in Use
```bash
# Find process
netstat -ano | findstr :5173

# Kill process
taskkill /PID <PID> /F
```

#### Vite Cache Issues
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

#### Firebase Errors
- Verify Firebase configuration in `.env`
- Check that Firebase project is active
- Ensure API keys are correct

#### API Connection Failed
- Verify backend is running on port 3000
- Check `VITE_BACKEND_URL` in `.env`
- Check browser console for CORS errors

#### Build Failures
```bash
# Check for type errors
npm run build

# Fix linting issues
npm run lint
npm run lint:fix
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_BACKEND_URL` | Yes | Backend API base URL |
| `VITE_ML_SERVER_URL` | Yes | ML OCR service base URL |
| `VITE_FIREBASE_API_KEY` | No | Firebase API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | No | Firebase auth domain |
| `VITE_FIREBASE_PROJECT_ID` | No | Firebase project ID |
| `VITE_APP_NAME` | No | Application display name |

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Dependencies

### Core

- **react** - UI library
- **react-dom** - DOM rendering
- **react-router-dom** - Client-side routing
- **vite** - Build tool and dev server

### Styling

- **tailwindcss** - Utility-first CSS framework
- **postcss** - CSS processing

### Authentication

- **firebase** - Authentication and user management

### UI Components

- **@radix-ui/*** - Accessible component primitives
- **class-variance-authority** - Component variants
- **clsx** / **tailwind-merge** - Conditional class names
- **lucide-react** - Icon library

### Utilities

- **axios** - HTTP client
- **react-icons** - Icon collection
- **react-hot-toast** - Toast notifications
