# Configuration Guide

## IP Address Configuration

### **IMPORTANT**

Before using Photo Gallery Pro, you **MUST** update the IP address configuration to match your NAS network settings.

### Step 1: Find Your NAS IP Address

```bash
# Method 1: Check NAS admin panel
# Control Panel > Network & File Services > Network Access

# Method 2: Command line
ip addr show | grep inet

# Method 3: Router admin panel
# Check connected devices list
```

### Step 2: Update Frontend Configuration

**Edit the file:** `frontend/index.html`

**Find line ~104:**
```javascript
const API_BASE_URL = 'http://192.168.1.100:5050/api';
```

**Replace with your NAS IP:**
```javascript
// Example IPs:
const API_BASE_URL = 'http://192.168.1.50:5050/api';   // Home network
const API_BASE_URL = 'http://192.168.0.100:5050/api';  // Alternative range
const API_BASE_URL = 'http://10.0.0.50:5050/api';      // Corporate network
```

### Step 3: Verify Configuration

After updating the IP address, test the connection:

```bash
# Test backend API
curl http://YOUR_NAS_IP:5050/api/test

# Expected response:
# {"success": true, "message": "Backend works!", ...}
```

## Advanced Configuration

### Custom Photos Directory

**Edit:** `backend/app.py`

```python
# Line 15
PHOTOS_PATH = "/share/Photos"  # Default

# Change to your custom path
PHOTOS_PATH = "/share/MyPhotos"
PHOTOS_PATH = "/share/CACHEDEV1_DATA/Pictures"
```

### Custom Port Configuration

**Backend Port:**
```python
# Edit backend/app.py line ~200
port = 5050  # Change to desired port
```

**Frontend Configuration:**
```javascript
// Update frontend/index.html accordingly
const API_BASE_URL = 'http://YOUR_NAS_IP:YOUR_PORT/api';
```

### Network Security

**Firewall Configuration:**
```bash
# Allow port 5050 for backend
# QNAP Control Panel > Network & File Services > Security > Firewall
# Add rule: Allow TCP port 5050
```

**Access Restriction:**
```python
# Edit backend/app.py CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://192.168.1.0/24"],  # Restrict to local network
        "methods": ["GET"],  # Read-only access
        "allow_headers": ["Content-Type"]
    }
})
```

## Troubleshooting Configuration

### Common IP Address Issues

**Problem:** Frontend shows "Cannot load photos"

**Solution:**
1. Check if IP address in `frontend/index.html` is correct
2. Verify backend is running: `ps aux | grep python3`
3. Test API directly: `curl http://YOUR_IP:5050/api/test`

**Problem:** "Connection refused" error

**Solution:**
1. Check if backend is running on correct port
2. Verify firewall allows port 5050
3. Check NAS network settings

### Network Discovery

**Find NAS on network:**
```bash
# Scan local network
nmap -sn 192.168.1.0/24

# Look for QNAP devices
arp -a | grep -i qnap
```

### Configuration Validation

**Check configuration files:**
```bash
# Verify IP in frontend
grep -n "API_BASE_URL" /share/CACHEDEV1_DATA/Web/gallery/frontend/index.html

# Verify photos path in backend
grep -n "PHOTOS_PATH" /share/CACHEDEV1_DATA/Web/gallery/backend/app.py

# Test backend configuration
cd /share/CACHEDEV1_DATA/Web/gallery/backend
python3 -c "from app import PHOTOS_PATH; print(f'Photos path: {PHOTOS_PATH}')"
```

## Example Configurations

### Home Network Setup
```javascript
// Typical home router setup
const API_BASE_URL = 'http://192.168.1.100:5050/api';
```

### Office Network Setup
```javascript
// Corporate network
const API_BASE_URL = 'http://10.0.1.50:5050/api';
```

### Custom Port Setup
```javascript
// Non-standard port
const API_BASE_URL = 'http://192.168.1.100:8080/api';
```

---

**Remember: Always restart the backend service after making configuration changes.**

```bash
# Restart backend
killall python3
cd /share/CACHEDEV1_DATA/Web/gallery/backend
python3 app.py production > /tmp/gallery.log 2>&1 &
```