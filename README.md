# Gallery Chatbot

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.8-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A modern web application that combines image gallery functionality with an AI-powered chatbot interface. This project allows users to upload, view, and interact with images while engaging in natural conversations about the visual content.

## 🌟 Features

- **Image Gallery**: Browse and view uploaded images in an organized gallery interface
- **Image Upload**: Support for uploading and managing images
- **AI Chatbot**: Interactive chatbot that can discuss and analyze images
- **Modern UI**: Clean and responsive user interface built with modern web technologies
- **Vector Database**: Efficient image storage and retrieval using vector database technology

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gallery-chatbot.git
cd gallery-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
API_KEY=your_api_key_here
IMAGE_DATA_FILE_PATH=path/to/image/storage
```

## 💻 Usage

1. Start the application:
```bash
python -m app.main
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

3. You can now:
   - Upload images through the upload interface
   - Browse the image gallery
   - Interact with the AI chatbot about the images

## 📁 Project Structure

```
gallery-chatbot/
├── app/
│   ├── api/            # API routes and endpoints
│   ├── config/         # Configuration settings
│   ├── services/       # Business logic and services
│   ├── static/         # Static files (CSS, JS, images)
│   ├── templates/      # HTML templates
│   ├── utils/          # Utility functions
│   ├── vectrodb_models/# Vector database models
│   └── main.py         # Application entry point
├── tests/              # Test files
├── .env               # Environment variables
├── requirements.txt   # Project dependencies
└── README.md         # Project documentation
```

## 🛠️ Technologies Used

- **Backend Framework**: FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Database**: Vector Database for image storage
- **AI/ML**: 
  - CLIP for image understanding
  - LangChain for chatbot functionality
- **Other Key Libraries**:
  - uvicorn (ASGI server)
  - python-multipart (file uploads)
  - jinja2 (templating)

[//]: # (## 🤝 Contributing)

[//]: # ()
[//]: # (Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.)

[//]: # ()
[//]: # (1. Fork the repository)

[//]: # (2. Create your feature branch &#40;`git checkout -b feature/AmazingFeature`&#41;)

[//]: # (3. Commit your changes &#40;`git commit -m 'Add some AmazingFeature'`&#41;)

[//]: # (4. Push to the branch &#40;`git push origin feature/AmazingFeature`&#41;)

[//]: # (5. Open a Pull Request)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for CLIP model
- FastAPI team for the excellent web framework
- All contributors and users of this project

---

Made with ❤️ by [Saib Ahmed Emil] 