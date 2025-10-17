# Use Python alpine for simple static file serving
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Copy website files
COPY src/ /app/

# Create non-root user
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER 1001

# Expose port 8080
EXPOSE 8080

# Start Python HTTP server
CMD ["python", "-m", "http.server", "8080"]