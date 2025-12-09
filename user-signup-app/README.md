# User Signup Application for GenAIOps Lab

A web application for managing workshop user sign-ups and distributing lab credentials. Participants provide their email address and receive a unique username (user1-user25), password, cluster domain, and lab instructions link.

## Features

- Email-based user registration
- Automatic user allocation (user1 through user25)
- Prevents duplicate registrations (same email gets same username)
- Maximum 25 user slots
- Real-time availability tracking
- SQLite database for persistence
- Containerized for easy deployment
- Configurable via environment variables

## Configuration

The application is configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `CLUSTER_DOMAIN` | The OpenShift cluster domain | `example.com` |
| `USER_PASSWORD` | Password for all users | `changeme` |
| `MAX_USERS` | Maximum number of users (1-100) | `25` |
| `LAB_INSTRUCTIONS_URL` | URL to lab instructions | `https://rhoai-genaiops.github.io/lab-instructions/` |
| `DB_PATH` | Path to SQLite database | `/data/users.db` |
| `ADMIN_TOKEN` | Secret token for admin endpoints | `admin-secret-token-change-me` |

## Quick Start

### Option 1: Docker Compose (Recommended for Testing)

1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```bash
   CLUSTER_DOMAIN=apps.your-cluster.example.com
   USER_PASSWORD=YourSecurePassword123
   MAX_USERS=25
   ```

3. Build and run:
   ```bash
   docker-compose up -d
   ```

4. Access the application at `http://localhost:8080`

### Option 2: Docker CLI

1. Build the image:
   ```bash
   docker build -t user-signup:latest .
   ```

2. Run the container:
   ```bash
   docker run -d \
     -p 8080:8080 \
     -e CLUSTER_DOMAIN=apps.your-cluster.example.com \
     -e USER_PASSWORD=YourSecurePassword123 \
     -e MAX_USERS=25 \
     -v user-signup-data:/data \
     --name user-signup \
     user-signup:latest
   ```

3. Access the application at `http://localhost:8080`

### Option 3: OpenShift/Kubernetes Deployment

1. Build and push the container image:
   ```bash
   # Build the image
   docker build -t quay.io/your-username/user-signup:latest .

   # Push to registry (e.g., Quay.io)
   docker push quay.io/your-username/user-signup:latest
   ```

2. Update the deployment YAML:
   ```bash
   # Edit openshift-deployment.yaml
   # Update the image reference and secret values
   ```

3. Deploy to OpenShift:
   ```bash
   oc apply -f openshift-deployment.yaml
   ```

4. Get the route URL:
   ```bash
   oc get route user-signup -n user-signup
   ```

## Customizing Configuration for OpenShift

Before deploying to OpenShift, edit `openshift-deployment.yaml` and update the Secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: user-signup-config
  namespace: user-signup
type: Opaque
stringData:
  CLUSTER_DOMAIN: "apps.your-actual-cluster.com"
  USER_PASSWORD: "YourSecurePassword123"
  MAX_USERS: "25"
  LAB_INSTRUCTIONS_URL: "https://rhoai-genaiops.github.io/lab-instructions/"
```

Also update the image in the Deployment section:

```yaml
spec:
  containers:
  - name: user-signup
    image: quay.io/your-username/user-signup:latest  # Update this
```

## API Endpoints

### `GET /`
Main registration page with HTML form.

### `POST /signup`
Register a user with an email address.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "username": "user1",
  "password": "YourPassword123",
  "cluster_domain": "apps.cluster.example.com",
  "lab_url": "https://rhoai-genaiops.github.io/lab-instructions/",
  "instructions": "Access the lab instructions at ... and use your credentials to log into the cluster."
}
```

**Error Response (400):**
```json
{
  "error": "All users have been assigned. No more slots available."
}
```

### `GET /stats`
Get current registration statistics.

**Response:**
```json
{
  "assigned": 15,
  "available": 10,
  "total": 25
}
```

## Admin Endpoints

### `GET /admin/users`
List all registered users (requires authentication).

**Authentication:**
- Via Authorization header: `Authorization: Bearer YOUR_ADMIN_TOKEN`
- Via query parameter: `?token=YOUR_ADMIN_TOKEN`

**Example:**
```bash
# Using curl with Authorization header
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" http://localhost:8080/admin/users

# Using curl with query parameter
curl "http://localhost:8080/admin/users?token=YOUR_ADMIN_TOKEN"
```

**Response:**
```json
{
  "total": 3,
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "user1",
      "password": "YourPassword123",
      "cluster_domain": "apps.cluster.example.com",
      "assigned_at": "2025-01-15 10:30:00"
    }
  ],
  "config": {
    "max_users": 25,
    "cluster_domain": "apps.cluster.example.com",
    "password": "YourPassword123",
    "lab_url": "https://rhoai-genaiops.github.io/lab-instructions/"
  }
}
```

### `GET /admin/export`
Export all registered users as CSV (requires authentication).

**Authentication:** Same as `/admin/users`

**Example:**
```bash
# Download CSV file
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  http://localhost:8080/admin/export -o users.csv

# Or with query parameter
curl "http://localhost:8080/admin/export?token=YOUR_ADMIN_TOKEN" -o users.csv
```

**CSV Format:**
```csv
Email,Username,Password,Cluster Domain,Assigned At
user1@example.com,user1,YourPassword123,apps.cluster.example.com,2025-01-15 10:30:00
user2@example.com,user2,YourPassword123,apps.cluster.example.com,2025-01-15 10:35:00
```

## Data Persistence

The application uses SQLite for data persistence. User assignments are stored in `/data/users.db` inside the container.

**Important:** Mount a volume to `/data` to persist user assignments across container restarts:

```bash
# Docker
-v user-signup-data:/data

# Docker Compose
volumes:
  - user-signup-data:/data

# Kubernetes/OpenShift
Use a PersistentVolumeClaim (already configured in openshift-deployment.yaml)
```

## Resetting the Database

To reset all user assignments:

1. Stop the application
2. Delete the database file or volume
3. Restart the application

**Docker:**
```bash
docker-compose down
docker volume rm user-signup_user-data
docker-compose up -d
```

**OpenShift:**
```bash
oc delete pvc user-signup-data -n user-signup
oc delete pod -l app=user-signup -n user-signup
# The PVC will be recreated automatically
```

## Monitoring

Check application logs:

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

## Troubleshooting

### Container won't start
- Check environment variables are set correctly
- Ensure port 8080 is not in use
- Check logs for errors

### Database errors
- Ensure `/data` directory is writable
- Check volume permissions
- Verify PVC is bound (for Kubernetes/OpenShift)

### All slots showing as taken
- Check the stats endpoint: `curl http://localhost:8080/stats`
- Reset the database if needed (see above)

### Email already registered
If a user re-submits their email, they receive the same username they were originally assigned. This prevents users from claiming multiple slots.

## Development

Run locally without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CLUSTER_DOMAIN=apps.test.com
export USER_PASSWORD=testpass
export MAX_USERS=25
export DB_PATH=./users.db

# Run the application
python app.py
```

Access at `http://localhost:8080`

## Security Considerations

1. **Admin Token**: Change the default `ADMIN_TOKEN` before deploying to production. Use a strong, random token.
   ```bash
   # Generate a secure random token
   openssl rand -base64 32
   ```
2. **Password Security**: The same password is shared among all users. Ensure this is acceptable for your use case.
3. **HTTPS**: Always use HTTPS in production (handled by OpenShift Route)
4. **Email Validation**: Basic validation is performed, but consider additional verification if needed
5. **Rate Limiting**: Consider adding rate limiting for production deployments
6. **Secrets Management**: Use Kubernetes/OpenShift Secrets for sensitive data (ADMIN_TOKEN, USER_PASSWORD)

### Setting a Secure Admin Token

**For Docker/Docker Compose:**
```bash
# Generate a secure token
export ADMIN_TOKEN=$(openssl rand -base64 32)

# Add to .env file
echo "ADMIN_TOKEN=$ADMIN_TOKEN" >> .env

# Or pass directly to docker run
docker run -d -e ADMIN_TOKEN="$ADMIN_TOKEN" ...
```

**For OpenShift:**
```bash
# Generate a secure token
ADMIN_TOKEN=$(openssl rand -base64 32)

# Update the secret in your deployment
oc create secret generic user-signup-config \
  --from-literal=ADMIN_TOKEN="$ADMIN_TOKEN" \
  --from-literal=CLUSTER_DOMAIN="apps.your-cluster.com" \
  --from-literal=USER_PASSWORD="YourPassword123" \
  --from-literal=MAX_USERS="25" \
  --from-literal=LAB_INSTRUCTIONS_URL="https://rhoai-genaiops.github.io/lab-instructions/" \
  -n user-signup \
  --dry-run=client -o yaml | oc apply -f -
```

## License

This application is provided as-is for workshop and educational purposes.
