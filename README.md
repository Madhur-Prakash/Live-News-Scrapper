# Live News Scrapper
**A Live News Web Scrapper**

---

## Overview
This repository implements a live news web scrapper that extracts news from various live websites. Users can choose to receive both national and international news based on their preferences.

---

## Features
- **National and International News**: Get news from various sources, both national and international.
- **Live Updates**: Receive live updates on the latest news.
- **Customizable**: Choose the type of news you want to receive.

---

## Technology Stack
- **Backend Framework**: FastAPI
- **Programming Language**: Python
- **Web Scraping Library**: BeautifulSoup

---

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:Madhur-Prakash/Live-News-Scrapper.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Live-News-Scrapper
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
--- 

## Alternative Installation using Docker
1. Ensure you have Docker and Docker Compose installed on your machine.

2. Navigate to the project directory:
   ```bash
   cd Live-News-Scrapper
   ```
   
3. Build and start the Docker container:
   ```bash
   docker-compose up --build
   ```

---

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```
2. Access the API documentation at:
   ```bash
   http://127.0.0.1:8000/docs
   ```
3. Use the API to get national and international news.

---

## API Endpoints

### News Endpoints
- **GET /news/national**: Get national news.
- **GET /news/international**: Get international news.

---

## Project Structure

```plaintext
Live-News-Scrapper/
├── .dockerignore
├── .gitignore  # gitignore file for GitHub
├── Dockerfile
├── LICENSE
├── README.md  # Project documentation
├── __init__.py  # initializes package
├── app.py  # main FastAPI app
├── docker-compose.yml
├── requirements.txt
└── scrapper
    ├── __init__.py  # initializes package
    ├── config
    │   └── config.py
    ├── helper
    │   └── utils.py
    ├── models
    │   └── models.py  # models
    └── src
        └── web_news.py
```

---

## Future Enhancements
- Add support for more news sources.
- Implement a scheduling system to update news regularly.
- Enhance the user interface to make it more user-friendly.

---

## Contribution Guidelines

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and submit a pull request.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author
**Madhur-Prakash**  
[GitHub](https://github.com/Madhur-Prakash)