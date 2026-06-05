# FreteBR Frontend

React + TypeScript + Vite + Tailwind CSS application for the FreteBR freight management platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite 5** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client for API calls

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   └── ProtectedRoute.tsx
│   ├── context/             # React Context providers
│   │   └── AuthContext.tsx
│   ├── pages/               # Page components
│   │   ├── LoginPage.tsx
│   │   ├── SignupPage.tsx
│   │   └── DashboardPage.tsx
│   ├── services/            # API services
│   │   └── api.ts
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility functions
│   ├── styles/              # Global styles
│   ├── App.tsx              # Main app component with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Tailwind directives
├── public/                  # Static assets
├── Dockerfile              # Multi-stage Docker build
├── nginx.conf              # Nginx configuration for SPA routing
├── docker-compose.yml      # (parent) includes frontend service
├── tailwind.config.js      # Tailwind configuration
├── postcss.config.js       # PostCSS configuration
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite configuration

```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Local Development

```bash
# Install dependencies
npm install

# Create .env.local (copy from .env.example)
cp .env.example .env.local

# Start dev server with HMR
npm run dev
```

The app will be available at `http://localhost:5173` (Vite default port)

### Building

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8000/api
```

## Features

- **Authentication System** - Signup/Login with JWT tokens
- **Protected Routes** - Dashboard only accessible to authenticated users
- **Responsive Design** - Mobile-first Tailwind CSS styling
- **API Integration** - Axios client with auth header injection
- **Type Safety** - Full TypeScript support

## API Endpoints Used

- `POST /auth/signup` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/me` - Get current user info

## Docker

### Build Docker Image

```bash
docker build -t fretebr-frontend:latest .
```

### Run with Docker

```bash
docker run -p 3000:3000 \
  -e VITE_API_URL=http://backend:8000/api \
  fretebr-frontend:latest
```

### Docker Compose

```bash
cd ..
docker-compose up frontend
```

Frontend will be available at `http://localhost:3000`

## Development Workflow

### Hot Module Replacement (HMR)

Vite provides instant HMR - changes to code are reflected in the browser without full page reload.

### Linting

```bash
npm run lint
```

### Authentication Flow

1. User visits `/` → redirects to `/dashboard`
2. If not authenticated → redirects to `/login`
3. User signs up at `/signup` or logs in at `/login`
4. JWT token stored in `localStorage`
5. Token automatically added to all API requests
6. On logout, token removed and user redirected to `/login`

## Deployment

The application is containerized and ready for deployment:

- Vite builds a static SPA (Single Page Application)
- Nginx serves the static files with proper SPA routing
- Listens on port 3000

See parent `DEPLOYMENT.md` for full deployment instructions.
