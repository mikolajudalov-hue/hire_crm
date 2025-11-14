# Digital Ocean Deployment Guide for Flask Application

This guide provides step-by-step instructions for deploying your Flask application to Digital Ocean using Docker.

## Prerequisites

Before you begin, ensure you have the following:

1.  **Digital Ocean Account:** An active account with Digital Ocean.
2.  **Digital Ocean Droplet:** A Linux server (Droplet) created on Digital Ocean (e.g., Ubuntu 22.04).
3.  **SSH Access:** The ability to connect to your Droplet via SSH.
4.  **Digital Ocean CLI (`doctl`):** (Optional, but recommended) Installed and configured on your local machine.
5.  **Docker and Docker Compose:** Installed on your Digital Ocean Droplet.

## Step 1: Install Docker and Docker Compose on the Droplet

Connect to your Droplet via SSH and run the following commands to install Docker and Docker Compose.

### Install Docker

\`\`\`bash
# Update the package list
sudo apt update

# Install necessary packages to allow apt to use a repository over HTTPS
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Add your user to the docker group to run Docker without sudo
sudo usermod -aG docker $USER
# You will need to log out and log back in for this to take effect
\`\`\`

### Install Docker Compose

\`\`\`bash
# Download the current stable release of Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.27.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Apply executable permissions to the binary
sudo chmod +x /usr/local/bin/docker-compose

# (Optional) Create a symbolic link for 'docker-compose'
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
\`\`\`

## Step 2: Transfer Project Files

Transfer the entire `project2` directory to your Droplet. You can use `scp` from your local machine:

\`\`\`bash
# Replace <your_droplet_ip> with your Droplet's IP address
scp -r project2/ user@<your_droplet_ip>:/home/user/
\`\`\`

## Step 3: Configure Environment Variables

Your application uses a `.env` file. For production, you should secure these variables.

1.  SSH into your Droplet and navigate to the project directory:
    \`\`\`bash
    cd project2
    \`\`\`
2.  Edit the `.env` file with your production-ready secrets and configurations.

## Step 4: Build and Run the Docker Container

1.  In the `project2` directory on your Droplet, build the Docker image:
    \`\`\`bash
    docker build -t my-flask-app .
    \`\`\`
2.  Run the container. The `-d` flag runs it in detached mode (background), and `-p 80:8080` maps the container's port 8080 (where Gunicorn is running) to the Droplet's public port 80 (standard HTTP):
    \`\`\`bash
    docker run -d --name flask-prod -p 80:8080 --restart always my-flask-app
    \`\`\`

    *   **`--restart always`**: Ensures the container restarts automatically if it crashes or the Droplet reboots.

## Step 5: Access Your Application

Your application should now be running and accessible via your Droplet's public IP address in a web browser.

## Project Files Summary

The following files were added or modified to enable Docker deployment:

| File Name | Purpose |
| :--- | :--- |
| `requirements.txt` | Added `gunicorn` for production serving. |
| `Dockerfile` | Defines the environment and steps to build the application image. |
| `.dockerignore` | Excludes unnecessary files from the Docker build context. |
| `docker-compose.yml` | Simple configuration for local testing and development. |
| `DEPLOYMENT_GUIDE.md` | This document. |
