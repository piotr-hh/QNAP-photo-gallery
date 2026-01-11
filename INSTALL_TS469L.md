# Photo Gallery Installation for QNAP TS-469L

## System Requirements
- QNAP TS-469L NAS Server
- Firmware Version: 4.3.4.2814 or newer
- **Python 3.8 or newer** (required for Flask 2.3.3 and Pillow 10.0.1)
- Web Server (built-in or Apache)

## Installation Steps

### 1. Enable SSH
```bash
# Access NAS admin panel
# Control Panel > Network & File Services > Telnet/SSH
# Enable SSH service on port 22
```

### 2. Install Python 3.8+

#### Method 1: Entware (Recommended)
```bash
# Check system architecture first
uname -m

# Install Entware for x86_64
wget -O - http://bin.entware.net/x64-k3.2/installer/generic.sh | /bin/sh

# Create symlink for /opt
rm -rf /opt
ln -s /share/CACHEDEV1_DATA/entware /opt

# Add to PATH
export PATH="/opt/bin:/opt/sbin:$PATH"
echo 'export PATH="/opt/bin:/opt/sbin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Update package list
opkg update

# Install Python 3.8+
opkg install python3 python3-pip

# Verify installation
python3 --version
```

#### Troubleshooting Entware
```bash
# If "cannot execute binary file" error
# Check architecture
uname -m

# For x86_64 systems
wget -O - http://bin.entware.net/x64-k3.2/installer/generic.sh | /bin/sh

# Always create symlink after installation
rm -rf /opt
ln -s /share/CACHEDEV1_DATA/entware /opt
export PATH="/opt/bin:/opt/sbin:$PATH"
```

### 3. Create Directory Structure
```bash
# Connect via SSH
# Replace 192.168.1.100 with your actual NAS IP address
ssh admin@192.168.1.100

# Create application directory
mkdir -p /share/CACHEDEV1_DATA/Web/gallery
mkdir -p /share/CACHEDEV1_DATA/Web/gallery/backend
mkdir -p /share/CACHEDEV1_DATA/Web/gallery/frontend

# Set permissions
chmod 755 /share/CACHEDEV1_DATA/Web/gallery
```

### 4. Upload Files
```bash
# Copy backend files to:
# /share/CACHEDEV1_DATA/Web/gallery/backend/
# - app.py
# - requirements.txt
# - start_nas.py

# Copy frontend files to:
# /share/CACHEDEV1_DATA/Web/gallery/frontend/
# - index.html
# - style.css
```

### 5. Install Python Dependencies
```bash
# Verify Python version first
python3 --version
# Should be 3.8 or newer

cd /share/CACHEDEV1_DATA/Web/gallery/backend

# Install dependencies
pip3 install -r requirements.txt
```

### 6. Configure IP Address

**IMPORTANT: You must update the IP address in the frontend before first use**

```bash
# Edit the frontend configuration
vi /share/CACHEDEV1_DATA/Web/gallery/frontend/index.html

# Find line ~104 and change the IP address
# const API_BASE_URL = 'http://192.168.1.100:5050/api';
# Replace 192.168.1.100 with your actual NAS IP
```

### 7. Configure Web Server
```bash
# For built-in web server
# Control Panel > Applications > Web Server
# Enable Web Server
# Document root: /share/Web (default)

# Create symbolic link for shorter URL
ln -s /share/CACHEDEV1_DATA/Web/gallery /share/Web/gallery
```

### 8. Start Backend Service
```bash
cd /share/CACHEDEV1_DATA/Web/gallery/backend
python3 app.py production > /tmp/gallery.log 2>&1 &
```

### 9. Access Application

**Important: Replace `192.168.1.100` with your actual NAS IP address**

```
# Web Interface
http://192.168.1.100/gallery/

# Backend API
http://192.168.1.100:5050/api/test
```

## Configuration

### Photo Directory
```bash
# Default path
/share/Photos

# To change, edit app.py line 15
PHOTOS_PATH = "/share/Photos"
```

### Port Configuration
```bash
# Default port: 5050
# To change, edit start_nas.py
```

## Manual Startup

Since autostart can be complex on QNAP systems, manual startup is recommended:

```bash
# Start backend manually
cd /share/CACHEDEV1_DATA/Web/gallery/backend
python3 app.py production > /tmp/gallery.log 2>&1 &

# Check if running
ps aux | grep python3
netstat -tlnp | grep 5050

# Stop when needed
killall python3
```

## Troubleshooting

### Python Version Issues

#### Check Python version
```bash
python3 --version
```

#### If Python < 3.8

**Use compatible library versions**
```bash
# Use legacy requirements
pip3 install -r requirements-legacy.txt

# Contents of requirements-legacy.txt
# Flask==2.2.5 (supports Python 3.7+)
# Flask-CORS==3.0.10
# Pillow==9.5.0 (supports Python 3.7+)
```

### Check Service Status
```bash
ps aux | grep python3
netstat -tlnp | grep 5050
```

### View Logs
```bash
tail -f /tmp/gallery.log
```

### Common Issues

#### Port 5050 already in use
```bash
# Check what's using the port
netstat -tlnp | grep 5050

# Kill process using port
killall python3
```

#### Photos not loading
```bash
# Check photos directory
ls -la /share/Photos

# Check permissions
chmod -R 755 /share/Photos
```

#### Backend not accessible
```bash
# Check if backend is running
ps aux | grep app.py

# Check logs for errors
tail -20 /tmp/gallery.log

# Restart backend
cd /share/CACHEDEV1_DATA/Web/gallery/backend
python3 app.py production > /tmp/gallery.log 2>&1 &
```

## Performance Tips

### For Large Photo Collections
- Organize photos in subfolders
- Use supported formats (JPEG recommended)
- Ensure sufficient RAM for thumbnail generation

### Network Optimization
- Use wired connection for better performance
- Consider photo resolution for web viewing

## Security Notes
- Change default passwords
- Enable firewall rules if needed
- Regular updates
- Restrict access to trusted networks

## Tested Configuration
- QNAP TS-469L
- Firmware 4.3.4.2814
- Python 3.11.10 via Entware
- 45 photos in multiple folders
- Chrome, Firefox, Safari browsers