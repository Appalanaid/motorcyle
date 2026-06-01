# 🚀 AWS Deployment Guide - Complete Step-by-Step

## 📋 OVERVIEW

Deploy your motorcycle recommendation system to AWS with:
- **Backend**: FastAPI on EC2 + RDS (SQL Server)
- **Frontend**: React on CloudFront + S3
- **Total Cost**: ~$20-50/month (free tier eligible)

---

## 🎯 DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                    AWS CLOUD                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────┐      ┌──────────────────┐     │
│  │   CloudFront     │      │   API Gateway    │     │
│  │   (Frontend)     │      │   (Optional)     │     │
│  └────────┬─────────┘      └────────┬─────────┘     │
│           │                         │                │
│  ┌────────▼─────────┐      ┌────────▼─────────┐     │
│  │   S3 Bucket      │      │   EC2 Instance   │     │
│  │  (React Build)   │      │  (FastAPI App)   │     │
│  └──────────────────┘      └────────┬─────────┘     │
│                                     │                │
│                            ┌────────▼─────────┐     │
│                            │   RDS (SQL Srv)  │     │
│                            │   (Database)     │     │
│                            └──────────────────┘     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 📦 PREREQUISITES

- AWS Account (free tier)
- AWS CLI installed
- Git repository (GitHub/GitLab)
- Domain name (optional)

### Install AWS CLI
```bash
# Windows PowerShell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

---

## 🔧 PHASE 1: AWS ACCOUNT SETUP

### Step 1.1: Create AWS Account
1. Go to https://aws.amazon.com
2. Click "Create AWS Account"
3. Complete registration
4. Create IAM user with EC2/RDS access

### Step 1.2: Create IAM User
```bash
# Use AWS Console to create user with policies:
# - AmazonEC2FullAccess
# - AmazonRDSFullAccess
# - AmazonS3FullAccess
# - CloudFrontFullAccess
```

### Step 1.3: Configure AWS CLI
```bash
aws configure
# Enter:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output: json
```

---

## 🗄️ PHASE 2: DATABASE SETUP (RDS)

### Step 2.1: Create RDS Instance

```bash
# Using AWS CLI
aws rds create-db-instance \
  --db-instance-identifier bike-db-prod \
  --db-instance-class db.t3.micro \
  --engine sqlserver-se \
  --master-username admin \
  --master-user-password "YourStrongPassword123!" \
  --allocated-storage 20 \
  --publicly-accessible \
  --region us-east-1
```

Or use AWS Console:
1. Go to RDS Dashboard
2. Click "Create database"
3. Select SQL Server
4. Choose `db.t3.micro` (free tier eligible)
5. Set master username/password
6. Create security group to allow port 1433

### Step 2.2: Get Database Endpoint
```bash
aws rds describe-db-instances \
  --db-instance-identifier bike-db-prod \
  --query 'DBInstances[0].Endpoint.Address'

# Output: bike-db-prod.xxxxx.us-east-1.rds.amazonaws.com
```

### Step 2.3: Initialize Database
```bash
# From your local machine, run:
python backend/init_db.py

# But first update config for RDS:
# DB_SERVER=bike-db-prod.xxxxx.us-east-1.rds.amazonaws.com
# DB_USER=admin
# DB_PASSWORD=YourStrongPassword123!
# USE_WINDOWS_AUTH=False (use SQL Auth for RDS)
```

---

## 🖥️ PHASE 3: EC2 BACKEND DEPLOYMENT

### Step 3.1: Launch EC2 Instance

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name my-key-pair \
  --security-groups default \
  --region us-east-1
```

Or use AWS Console:
1. EC2 Dashboard → Launch Instance
2. Select: Ubuntu 22.04 LTS
3. Instance type: t2.micro (free tier)
4. Security group: Allow ports 22 (SSH), 8000 (App)
5. Key pair: Create or select existing
6. Launch

### Step 3.2: Connect to EC2

```bash
# Get instance IP from AWS Console
# Then SSH:
ssh -i "path/to/key.pem" ubuntu@YOUR_EC2_IP

# Example:
ssh -i "C:\Keys\my-key.pem" ubuntu@54.123.45.67
```

### Step 3.3: Setup Backend on EC2

```bash
# On EC2 instance:

# Update system
sudo apt update
sudo apt upgrade -y

# Install Python & dependencies
sudo apt install -y python3 python3-pip python3-venv git

# Clone your repository
git clone https://github.com/YOUR_USERNAME/motorcycle-recommendation.git
cd motorcycle-recommendation/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with production values
cat > .env << 'EOF'
DB_SERVER=bike-db-prod.xxxxx.us-east-1.rds.amazonaws.com
DB_DATABASE=Bike_DB
DB_USER=admin
DB_PASSWORD=YourStrongPassword123!
USE_WINDOWS_AUTH=False

OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY
OPENAI_MODEL_VISION=gpt-4-vision-preview
OPENAI_MODEL_IMAGE=dall-e-3

DEBUG=False
APP_HOST=0.0.0.0
APP_PORT=8000
ALLOWED_ORIGINS=["http://YOUR_DOMAIN.com", "https://YOUR_DOMAIN.com"]

IMAGE_UPLOAD_DIR=/tmp/uploads
MAX_UPLOAD_SIZE=10485760
EOF

# Create uploads directory
mkdir -p /tmp/uploads
chmod 755 /tmp/uploads

# Test run
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Step 3.4: Setup Systemd Service (Auto-Start)

```bash
# Create service file
sudo bash -c 'cat > /etc/systemd/system/bike-api.service << "EOF"
[Unit]
Description=Motorcycle Recommendation API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/motorcycle-recommendation/backend
Environment="PATH=/home/ubuntu/motorcycle-recommendation/backend/venv/bin"
ExecStart=/home/ubuntu/motorcycle-recommendation/backend/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

# Enable and start service
sudo systemctl enable bike-api.service
sudo systemctl start bike-api.service

# Check status
sudo systemctl status bike-api.service
```

### Step 3.5: Setup Nginx (Reverse Proxy)

```bash
# Install Nginx
sudo apt install -y nginx

# Create config
sudo bash -c 'cat > /etc/nginx/sites-available/bike-api << "EOF"
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF'

# Enable site
sudo ln -s /etc/nginx/sites-available/bike-api /etc/nginx/sites-enabled/

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### Step 3.6: Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d YOUR_DOMAIN.com

# Auto-renewal enabled by default
sudo systemctl enable certbot.timer
```

---

## 🎨 PHASE 4: S3 + CLOUDFRONT FRONTEND DEPLOYMENT

### Step 4.1: Build Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Output: build/ folder with static files
```

### Step 4.2: Create S3 Bucket

```bash
# Using AWS CLI
aws s3 mb s3://my-bike-app-frontend-prod --region us-east-1

# Block public access (CloudFront will access it)
aws s3api put-public-access-block \
  --bucket my-bike-app-frontend-prod \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Step 4.3: Upload Build Files

```bash
# Sync build folder to S3
aws s3 sync ./build s3://my-bike-app-frontend-prod \
  --delete \
  --cache-control "max-age=31536000" \
  --exclude "index.html"

# Special handling for index.html (no cache)
aws s3 cp ./build/index.html s3://my-bike-app-frontend-prod \
  --cache-control "no-cache, no-store, must-revalidate"
```

### Step 4.4: Create CloudFront Distribution

Using AWS Console:
1. CloudFront → Create distribution
2. S3 bucket origin: `my-bike-app-frontend-prod`
3. Restrict bucket access: Yes (use OAI)
4. Default root object: `index.html`
5. Error handling: 404 → `index.html` (for routing)
6. Create

### Step 4.5: Update Frontend API URL

Before building, update `frontend/src/api-url.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.your-domain.com';
```

Build command:
```bash
REACT_APP_API_URL=https://api.your-domain.com npm run build
```

---

## 🔗 PHASE 5: DOMAIN & DNS SETUP

### Step 5.1: Get Domain
1. Register at: Route53, GoDaddy, Namecheap, etc.
2. Use AWS Route53 for easier setup

### Step 5.2: Setup DNS Records

```bash
# In AWS Route53:

# 1. Frontend (CloudFront)
Record: www.your-domain.com
Type: CNAME
Value: d123.cloudfront.net

# 2. Backend (EC2)
Record: api.your-domain.com
Type: A
Value: YOUR_EC2_PUBLIC_IP

# Or use Elastic IP (permanent IP for EC2)
aws ec2 allocate-address --region us-east-1
```

### Step 5.3: Verify SSL Certificates
```bash
# Check backend SSL
curl https://api.your-domain.com/health

# Check frontend
curl https://www.your-domain.com
```

---

## 📊 PHASE 6: MONITORING & LOGGING

### Step 6.1: CloudWatch Logs (Backend)

```bash
# On EC2, install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Step 6.2: RDS Monitoring

AWS Console → RDS → Database → Monitoring tab
- View CPU, Memory, Connections

### Step 6.3: EC2 Monitoring

AWS Console → EC2 → Instances → Monitoring tab
- View CPU, Network, Status checks

---

## 💰 PHASE 7: COST MANAGEMENT

### Free Tier Breakdown
```
EC2 t2.micro:           FREE (1 year)
RDS db.t3.micro:        FREE (1 year)
S3:                     5GB FREE (per month)
CloudFront:             50GB FREE (per month)
Data transfer:          1GB FREE (per month)

Total Monthly Cost After Free Tier:
≈ $20-40/month (t2.micro depreciation + data)
```

### Cost Optimization Tips

1. **Set up billing alerts**
```bash
AWS Console → Billing → Alerts → Set budget ($50)
```

2. **Use Savings Plans**
```bash
AWS Console → Savings Plans → Purchase 1-year plan
Saves ~20-30% on compute
```

3. **Monitor unused resources**
```bash
# Delete unneeded snapshots, volumes, IPs
aws ec2 describe-snapshots --owner-ids self
aws ec2 describe-volumes --filters Name=status,Values=available
```

---

## 🧪 PHASE 8: TESTING DEPLOYMENT

### Step 8.1: Test Backend
```bash
# Health check
curl https://api.your-domain.com/health

# API docs
curl https://api.your-domain.com/docs

# Test recommendation
curl -X POST https://api.your-domain.com/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"...","height_cm":180,"weight_kg":75}'
```

### Step 8.2: Test Frontend
1. Visit: https://www.your-domain.com
2. Upload image
3. Check if recommendation loads
4. Check Network tab for API calls

### Step 8.3: Load Testing
```bash
# Using Apache Bench
sudo apt install apache2-utils

ab -n 100 -c 10 https://api.your-domain.com/health

# Results show request/sec and response times
```

---

## 🚨 TROUBLESHOOTING

### Backend Not Responding
```bash
# SSH to EC2
ssh -i key.pem ubuntu@IP

# Check service status
sudo systemctl status bike-api.service

# View logs
sudo journalctl -u bike-api.service -f

# Test locally
curl http://127.0.0.1:8000/health
```

### Frontend Not Loading
```bash
# Check CloudFront distribution
aws cloudfront list-distributions

# Invalidate cache
aws cloudfront create-invalidation \
  --distribution-id E123456 \
  --paths "/*"

# Check S3 sync
aws s3 ls s3://my-bike-app-frontend-prod
```

### Database Connection Issues
```bash
# From EC2, test connection
python3 -c "
import pyodbc
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=bike-db-prod.xxxxx.us-east-1.rds.amazonaws.com;Database=Bike_DB;UID=admin;PWD=password')
print('Connected!')
"

# Check RDS security group
aws ec2 describe-security-groups
# Ensure port 1433 allows inbound from EC2 security group
```

---

## 📋 DEPLOYMENT CHECKLIST

- [ ] AWS Account created
- [ ] IAM user with proper permissions
- [ ] RDS SQL Server instance running
- [ ] EC2 instance running
- [ ] Backend code deployed to EC2
- [ ] FastAPI running via systemd
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Frontend built and uploaded to S3
- [ ] CloudFront distribution created
- [ ] DNS records configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Billing alerts set up
- [ ] Monitoring dashboards configured

---

## 🎉 DONE! DEPLOYMENT COMPLETE

**Your Application is Live!**

```
Frontend: https://www.your-domain.com
Backend API: https://api.your-domain.com
API Docs: https://api.your-domain.com/docs
```

### Next Steps:
1. Monitor CloudWatch dashboards
2. Set up automated backups
3. Configure auto-scaling (optional)
4. Plan disaster recovery
5. Update CI/CD pipeline (GitHub Actions)

---

## 📞 SUPPORT & RESOURCES

- AWS Docs: https://docs.aws.amazon.com/
- FastAPI on AWS: https://docs.aws.amazon.com/elasticbeanstalk/
- React on S3+CloudFront: https://aws.amazon.com/blogs/compute/hosting-a-static-website-using-aws-amplify/
- AWS Cost Calculator: https://calculator.aws/
