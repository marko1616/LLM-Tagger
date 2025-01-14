# 🚀 llm-tagger

## 📦 Installation

This project provides a Docker setup to deploy the application easily. Additionally, we offer a Python script to generate the necessary configuration file.

### 🛠️ Setup

1. **Install Docker and Docker-Compose**  
   Make sure you have Docker and Docker-Compose installed on your system.

2. **Generate Configuration File**  
   Run the following command to generate the configuration file:  
   ```bash
   python cli.py setup
   ```

3. **Build the Application**  
    Use the following command to build the application:
    ```bash
    docker compose build --no-cache
    ```

4. **Start the Application**  
   Use the following command to start the application:  
   ```bash
   docker compose up -d
   ```

5. **Build arguments**
    - `USE_MIRROR`: Set to `true` to use a mirror from [`ustc`](https://mirrors.ustc.edu.cn/) for `yarn` and `pip`. Default is `false`.  
    Example:
    ```bash
    docker compose build --build-arg USE_MIRROR=true
    ```

    - `PROXY`: Set the proxy server for `yarn` and `pip`.  
    Example:
    ```bash
    docker compose build --build-arg PROXY=http://your-proxy-server:port
    ```

---

Enjoy using **llm-tagger**! 🎉