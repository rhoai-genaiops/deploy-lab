# Administrator Guide

Quick reference guide for managing the User Signup Application.

## Quick Links

- **Main Page**: `https://your-app-url/`
- **Statistics**: `https://your-app-url/stats`
- **Admin Panel**: `https://your-app-url/admin/users?token=YOUR_TOKEN`
- **Export CSV**: `https://your-app-url/admin/export?token=YOUR_TOKEN`

## Common Admin Tasks

### 1. View All Registered Users

**Browser:**
```
https://your-app-url/admin/users?token=YOUR_ADMIN_TOKEN
```

**Command Line:**
```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" https://your-app-url/admin/users | jq
```

### 2. Export Users to CSV

**Download via Browser:**
```
https://your-app-url/admin/export?token=YOUR_ADMIN_TOKEN
```

**Command Line:**
```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  https://your-app-url/admin/export -o lab-users-$(date +%Y%m%d).csv
```

### 3. Check Current Statistics

**No authentication required:**
```bash
curl https://your-app-url/stats | jq
```

### 4. Reset All Registrations

**For Docker/Docker Compose:**
```bash
# Stop the application
docker-compose down

# Remove the database volume
docker volume rm user-signup_user-data

# Restart the application
docker-compose up -d
```

**For OpenShift:**
```bash
# Delete the PVC
oc delete pvc user-signup-data -n user-signup

# Delete the pod (it will restart and recreate the PVC)
oc delete pod -l app=user-signup -n user-signup

# Wait for new pod to be ready
oc wait --for=condition=ready pod -l app=user-signup -n user-signup --timeout=60s
```

### 5. Change Configuration

**Docker Compose:**
1. Edit `.env` file
2. Restart: `docker-compose restart`

**OpenShift:**
```bash
# Update the secret
oc edit secret user-signup-config -n user-signup

# Restart pods to pick up changes
oc rollout restart deployment/user-signup -n user-signup
```

### 6. View Application Logs

**Docker:**
```bash
docker logs -f user-signup
```

**Docker Compose:**
```bash
docker-compose logs -f
```

**OpenShift:**
```bash
oc logs -f deployment/user-signup -n user-signup
```

## Monitoring Workshop Progress

### Real-time Statistics Dashboard

Create a simple monitoring script:

```bash
#!/bin/bash
# monitor-lab.sh

API_URL="https://your-app-url"
ADMIN_TOKEN="your-admin-token"

while true; do
  clear
  echo "=== Lab Registration Monitor ==="
  echo "Time: $(date)"
  echo ""

  # Get stats
  curl -s "$API_URL/stats" | jq -r '"Registered: \(.assigned)/\(.total) (\(.available) available)"'

  echo ""
  echo "=== Recent Registrations ==="

  # Get latest users
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/admin/users" | \
    jq -r '.users[:5] | .[] | "[\(.assigned_at)] \(.username) - \(.email)"'

  sleep 10
done
```

### Email Distribution List

Extract all emails for communication:

```bash
curl -s -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  https://your-app-url/admin/users | \
  jq -r '.users[].email' | sort
```

### Generate User List for Printing

```bash
curl -s -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  https://your-app-url/admin/users | \
  jq -r '.users[] | "\(.username): \(.password) @ \(.cluster_domain)"'
```

## Security Best Practices

### 1. Generate Secure Admin Token

```bash
# Generate a 32-byte random token
openssl rand -base64 32
```

### 2. Rotate Admin Token

**Docker Compose:**
```bash
# Generate new token
NEW_TOKEN=$(openssl rand -base64 32)

# Update .env
sed -i "s/ADMIN_TOKEN=.*/ADMIN_TOKEN=$NEW_TOKEN/" .env

# Restart
docker-compose restart
```

**OpenShift:**
```bash
# Generate new token
NEW_TOKEN=$(openssl rand -base64 32)

# Update secret
oc patch secret user-signup-config -n user-signup \
  -p "{\"stringData\":{\"ADMIN_TOKEN\":\"$NEW_TOKEN\"}}"

# Restart deployment
oc rollout restart deployment/user-signup -n user-signup
```

### 3. Restrict Access

For OpenShift, limit access to the admin endpoints using NetworkPolicies or by exposing the admin endpoints on a separate route with OAuth.

## Troubleshooting

### Users Can't Register

1. Check if all slots are filled:
   ```bash
   curl https://your-app-url/stats
   ```

2. Check application logs for errors:
   ```bash
   # Docker
   docker logs user-signup

   # OpenShift
   oc logs deployment/user-signup -n user-signup
   ```

### Database Issues

1. Verify volume is mounted:
   ```bash
   # Docker
   docker inspect user-signup | grep Mounts -A 10

   # OpenShift
   oc describe pod -l app=user-signup -n user-signup | grep Mounts -A 10
   ```

2. Check database file permissions:
   ```bash
   # Docker
   docker exec user-signup ls -la /data/

   # OpenShift
   oc exec deployment/user-signup -n user-signup -- ls -la /data/
   ```

### Admin Endpoints Return 401

1. Verify admin token matches:
   ```bash
   # Docker
   docker exec user-signup env | grep ADMIN_TOKEN

   # OpenShift
   oc get secret user-signup-config -n user-signup -o jsonpath='{.data.ADMIN_TOKEN}' | base64 -d
   ```

2. Check token format in request (no extra spaces or newlines)

## Workshop Day Checklist

**Before the Workshop:**
- [ ] Deploy application and verify it's accessible
- [ ] Test registration flow end-to-end
- [ ] Verify admin endpoints work with your token
- [ ] Export initial stats (should be 0 users)
- [ ] Set up monitoring dashboard
- [ ] Share registration URL with participants

**During the Workshop:**
- [ ] Monitor registration progress
- [ ] Check logs for any errors
- [ ] Keep admin panel open for quick stats
- [ ] Help participants who have issues registering

**After the Workshop:**
- [ ] Export final user list as CSV
- [ ] Save database backup if needed
- [ ] Generate attendance report
- [ ] Reset database for next workshop (if applicable)

## Backup and Restore

### Backup Database

**Docker:**
```bash
docker cp user-signup:/data/users.db ./backup-$(date +%Y%m%d).db
```

**OpenShift:**
```bash
POD=$(oc get pod -l app=user-signup -n user-signup -o jsonpath='{.items[0].metadata.name}')
oc cp $POD:/data/users.db ./backup-$(date +%Y%m%d).db -n user-signup
```

### Restore Database

**Docker:**
```bash
# Stop container
docker stop user-signup

# Restore database
docker cp ./backup-20250115.db user-signup:/data/users.db

# Start container
docker start user-signup
```

**OpenShift:**
```bash
POD=$(oc get pod -l app=user-signup -n user-signup -o jsonpath='{.items[0].metadata.name}')

# Copy backup to pod
oc cp ./backup-20250115.db $POD:/data/users.db -n user-signup

# Restart pod
oc delete pod $POD -n user-signup
```

## Support

For issues or questions:
1. Check application logs
2. Review this guide
3. Consult the main README.md
4. Check OpenShift events: `oc get events -n user-signup`
