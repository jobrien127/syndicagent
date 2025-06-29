# 🐳 SyndicAgent Docker Guide

## 📋 Prerequisites

1. **Install Docker Desktop** (if not already installed):
   - Download from: https://www.docker.com/products/docker-desktop
   - Or install via Homebrew: `brew install --cask docker`

2. **Start Docker Desktop**:
   - Open Docker Desktop application
   - Wait for it to start (you'll see the Docker icon in the menu bar)

## 🚀 Quick Start

### Option 1: Using the Helper Script (Recommended)

```bash
# Make sure you're in the syndicagent directory
cd /Users/josephobrien/projects/full-stack/syndicagent

# Run the demo
./docker-run.sh demo

# Run tests
./docker-run.sh test

# Run pytest
./docker-run.sh pytest
```

### Option 2: Using Docker Compose Directly

```bash
# Change to docker directory
cd docker

# Run demo
docker-compose up --build syndicagent

# Run tests
docker-compose --profile test up --build syndicagent-test

# Run pytest
docker-compose --profile test up --build syndicagent-pytest
```

## 🔧 Available Commands

### Helper Script Commands:

```bash
./docker-run.sh demo       # Run the SyndicAgent demo
./docker-run.sh test       # Run comprehensive tests
./docker-run.sh pytest     # Run pytest unit tests
./docker-run.sh build      # Build Docker images
./docker-run.sh up         # Start all services (background)
./docker-run.sh down       # Stop all services
./docker-run.sh logs       # Show logs
./docker-run.sh shell      # Open shell in container
./docker-run.sh clean      # Clean up everything
./docker-run.sh help       # Show help
```

## 🌟 Docker Advantages

### ✅ **Benefits of Running in Docker:**
- **Consistent Environment**: Same environment across all machines
- **Redis Integration**: Includes Redis server automatically
- **PostgreSQL Database**: Full database setup included
- **Isolated Dependencies**: No conflicts with local Python setup
- **Easy Cleanup**: Remove everything with one command
- **Production-like**: Matches deployment environment

### 📊 **Services Included:**
- **syndicagent**: Main application container
- **redis**: Redis cache server
- **postgres**: PostgreSQL database
- **Volume persistence**: Data survives container restarts

## 🧪 Testing in Docker

### **Comprehensive Test Suite:**
```bash
./docker-run.sh test
```
**What it tests:**
- All module imports
- API client with Redis caching
- Data processing pipeline
- Report generation
- Error handling with database

### **Unit Tests:**
```bash
./docker-run.sh pytest
```
**What it covers:**
- Individual component tests
- Integration tests
- Mock data validation
- All data types processing

### **Demo Mode:**
```bash
./docker-run.sh demo
```
**What it shows:**
- Full system workflow
- Data collection → Processing → Reporting
- PDF generation with database storage
- Complete functionality demonstration

## 🔄 Development Workflow

### **1. Start Development Environment:**
```bash
./docker-run.sh up
```

### **2. View Logs:**
```bash
./docker-run.sh logs
```

### **3. Access Container Shell:**
```bash
./docker-run.sh shell
```

### **4. Run Tests:**
```bash
./docker-run.sh test
./docker-run.sh pytest
```

### **5. Clean Up:**
```bash
./docker-run.sh down
```

## 🌐 Environment Variables

### **With Real Agworld API:**
```bash
AGWORLD_API_TOKEN=your_token_here ./docker-run.sh demo
```

### **Using .env File:**
Create `.env` file in project root:
```bash
AGWORLD_API_TOKEN=your_token_here
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql://user:password@db:5432/agworld
```

## 📂 Volume Mounts

Docker containers mount local directories:
- `./output/` → `/app/output/` (Generated reports)
- `./logs/` → `/app/logs/` (Application logs)

Generated files will appear in your local directories!

## 🔍 Troubleshooting

### **Docker Not Running:**
```bash
# Check Docker status
docker info

# Start Docker Desktop
open /Applications/Docker.app
```

### **View Container Logs:**
```bash
./docker-run.sh logs
```

### **Access Container:**
```bash
./docker-run.sh shell
python test_local.py  # Run tests inside container
```

### **Clean Start:**
```bash
./docker-run.sh clean
./docker-run.sh build
./docker-run.sh demo
```

## 🎯 Docker vs Local Testing

| Feature | Local | Docker |
|---------|--------|--------|
| **Setup** | ✅ Ready now | ⚠️ Requires Docker |
| **Redis** | ❌ Manual install | ✅ Automatic |
| **Database** | ❌ SQLite only | ✅ PostgreSQL |
| **Isolation** | ❌ System deps | ✅ Containerized |
| **Production-like** | ❌ Dev environment | ✅ Production-like |
| **Cleanup** | ❌ Manual | ✅ One command |

## 📋 Next Steps

1. **Start Docker Desktop**
2. **Run the demo**: `./docker-run.sh demo`
3. **Check the output**: Look in `./output/` for generated reports
4. **Run tests**: `./docker-run.sh test` and `./docker-run.sh pytest`
5. **Configure API token**: Set `AGWORLD_API_TOKEN` for live data

## 🎉 Expected Results

When Docker is running, you should see:
```
✅ Redis cache working
✅ Database connections working
✅ All tests passing (7/7)
✅ PDF reports generated
✅ Full integration successful
```

The Docker setup provides the complete SyndicAgent environment with all dependencies and services ready to use!
