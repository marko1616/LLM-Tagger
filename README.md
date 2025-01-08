# llm-tagger

## Installation
This project provide docker to deploy the application and we provide a python script to generate the configuration file.

### setup
1. Install docker and docker-compose
2. Run the following command to generate the configuration file: `python cli.py setup`
3. Run the following command to start the application: `docker-compose up -d --build`