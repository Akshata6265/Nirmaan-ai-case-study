# Detailed Deployment Guide

## Table of Contents
1. [Local Deployment](#local-deployment)
2. [Cloud Deployment (AWS EC2)](#cloud-deployment-aws-ec2)
3. [Heroku Deployment](#heroku-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Local Deployment

### Prerequisites
- Python 3.8 or higher installed
- Git installed (optional, for cloning)
- Command Prompt or PowerShell (Windows) / Terminal (macOS/Linux)

### Step-by-Step Instructions

#### Step 1: Download/Clone the Project
```powershell
# If using Git
git clone <repository-url>
cd "Deepa Task"

# OR download ZIP and extract, then navigate to folder
cd "path\to\Deepa Task"
```

#### Step 2: Create Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt)
venv\Scripts\activate.bat

# On macOS/Linux
source venv/bin/activate
```

**Note**: If you get an execution policy error on Windows PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 3: Install Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Installation Time**: 5-15 minutes (depending on internet speed)

#### Step 4: Download NLP Models
```powershell
# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# The sentence-transformer model will download automatically on first run
```

#### Step 5: Verify Installation
```powershell
# Check if all packages are installed
pip list
```

You should see Flask, sentence-transformers, pandas, etc.

#### Step 6: Run the Application
```powershell
# Start the Flask server
python backend/app.py
```

**Expected Output**:
```
* Serving Flask app 'app'
* Debug mode: on
WARNING: This is a development server.
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

#### Step 7: Access the Application
1. Open your web browser
2. Navigate to: `http://localhost:5000` or `http://127.0.0.1:5000`
3. You should see the Communication Skills Scoring interface

#### Step 8: Test the Application
1. Copy a sample transcript from `data/rubric_data.xlsx`
2. Paste it into the text area
3. Click "Score Transcript"
4. View the results with overall score and per-criterion feedback

### Stopping the Server
```powershell
# In the terminal where the server is running
Press CTRL+C

# Deactivate virtual environment
deactivate
```

---

## Cloud Deployment (AWS EC2)

### Prerequisites
- AWS account with EC2 access
- Basic knowledge of SSH and Linux commands

### Step-by-Step Instructions

#### Step 1: Launch EC2 Instance
1. Log in to AWS Console
2. Navigate to EC2 Dashboard
3. Click "Launch Instance"
4. Configuration:
   - **AMI**: Ubuntu Server 22.04 LTS (Free Tier Eligible)
   - **Instance Type**: t2.micro (Free Tier)
   - **Key Pair**: Create or select existing key pair (.pem file)
   - **Security Group**: 
     - SSH (port 22) - Your IP
     - HTTP (port 80) - Anywhere
     - Custom TCP (port 5000) - Anywhere

#### Step 2: Connect to EC2 Instance
```bash
# On Windows (use Git Bash or WSL)
chmod 400 your-key.pem
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip

# On macOS/Linux
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

#### Step 3: Set Up Server Environment
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Clone your repository
git clone <your-repository-url>
cd "Deepa Task"
```

#### Step 4: Install Application Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Download NLP models
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

#### Step 5: Run Application (Production Mode)
```bash
# Install production server (Gunicorn)
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

#### Step 6: Keep Application Running (Using Screen or Systemd)

**Option A: Using Screen**
```bash
# Install screen
sudo apt install screen -y

# Start screen session
screen -S comm-app

# Run application
cd "Deepa Task"
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# Detach: Press CTRL+A then D
# Reattach later: screen -r comm-app
```

**Option B: Using Systemd Service**
```bash
# Create service file
sudo nano /etc/systemd/system/comm-scoring.service
```

Add this content:
```ini
[Unit]
Description=Communication Scoring System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Deepa Task
Environment="PATH=/home/ubuntu/Deepa Task/venv/bin"
ExecStart=/home/ubuntu/Deepa Task/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable comm-scoring
sudo systemctl start comm-scoring
sudo systemctl status comm-scoring
```

#### Step 7: Access Application
Open browser and navigate to: `http://your-ec2-public-ip:5000`

---

## Heroku Deployment

### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed

### Step-by-Step Instructions

#### Step 1: Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

#### Step 2: Create Required Files

**Procfile** (in project root):
```
web: gunicorn backend.app:app
```

**runtime.txt** (in project root):
```
python-3.11.6
```

#### Step 3: Deploy to Heroku
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Add Python buildpack
heroku buildpacks:set heroku/python

# Push to Heroku
git add .
git commit -m "Initial deployment"
git push heroku main

# Open application
heroku open
```

---

## Docker Deployment

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

### Step 2: Build and Run
```bash
# Build Docker image
docker build -t comm-scoring .

# Run container
docker run -p 5000:5000 comm-scoring

# Access at http://localhost:5000
```

---

## Troubleshooting

### Issue 1: Virtual Environment Activation Error (Windows)
**Error**: "cannot be loaded because running scripts is disabled"

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Port 5000 Already in Use
**Error**: "Address already in use"

**Solution**:
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in backend/app.py
```

### Issue 3: Module Not Found Error
**Error**: "ModuleNotFoundError: No module named 'flask'"

**Solution**:
```bash
# Ensure virtual environment is activated
# Check activation with:
which python  # macOS/Linux
where python  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 4: Slow First Load
**Cause**: Sentence-transformer model downloading (500MB+)

**Solution**: Wait for first download; subsequent runs are faster. Pre-download:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### Issue 5: Memory Error on Free Tier
**Solution**: 
- Use smaller model: `paraphrase-MiniLM-L3-v2`
- Reduce workers in Gunicorn: `-w 2` instead of `-w 4`

### Issue 6: CORS Error in Frontend
**Solution**: Ensure Flask-CORS is installed and configured in `backend/app.py`

---

## Performance Optimization

### For Production
1. Use Gunicorn with multiple workers
2. Enable caching for models
3. Use Redis for session management
4. Set up Nginx as reverse proxy
5. Enable gzip compression

### Nginx Configuration (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Monitoring and Logs

### View Application Logs
```bash
# Local
python backend/app.py  # logs in terminal

# Heroku
heroku logs --tail

# EC2 (with systemd)
sudo journalctl -u comm-scoring -f

# Docker
docker logs <container-id>
```

---

## Security Recommendations

1. **Never commit sensitive data** (API keys, passwords)
2. **Use environment variables** for configuration
3. **Enable HTTPS** in production
4. **Set up firewall rules** on cloud servers
5. **Regular security updates**: `sudo apt update && sudo apt upgrade`

---

## Support and Maintenance

### Regular Maintenance
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Monitor disk space: `df -h`
- Check logs regularly
- Backup data folder

### Getting Help
- Check GitHub Issues
- Review Flask documentation
- Sentence-transformers documentation

---

## Conclusion

This guide covers multiple deployment scenarios. For development and testing, local deployment is recommended. For production, cloud deployment with proper security and monitoring is advised.

**Recommended Path**:
1. Start with local deployment to test
2. Move to AWS/Heroku for public access
3. Add Docker for containerization and portability

For any issues not covered here, please open an issue on GitHub.
