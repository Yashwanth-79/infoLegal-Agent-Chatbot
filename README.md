
# 🏛️ Legal Research Assistant

## Overview

The Legal Research Assistant is an advanced AI-powered tool designed to help users retrieve and understand legal information from Indian legal documents. Utilizing CrewAI and Google's Gemini AI, this application provides intelligent legal research capabilities with an intuitive Streamlit interface.

## 🌟 Features

- **AI-Powered Legal Research**
  - Retrieve relevant legal sections from documents
  - Transform complex legal text into understandable summaries
  - Support for multiple PDF sources

- **Flexible Document Management**
  - Upload custom PDF files
  - Add PDF URLs
  - Manage document sources dynamically
  - Pre-loaded default legal documents

- **User-Friendly Interface**
  - Chat-based query input
  - Real-time document analysis
  - Query history tracking
  - Downloadable summaries and history

## 🛠️ Technology Stack

- **AI Framework**: CrewAI
- **Large Language Model**: Google Gemini 1.5 Pro
- **Web Framework**: Streamlit
- **Programming Language**: Python

## 📦 Prerequisites

- Python 3.8+
- Gemini API Key
- Internet connection

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/legal-research-assistant.git
cd legal-research-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🔧 Configuration

### Default PDF Sources
The application comes with two pre-loaded legal documents:
- ICAI PDF Document
- Litigation Guide for India

### Customization
- Add/remove PDF sources via the Streamlit sidebar
- Upload custom PDF files
- Add PDF URLs dynamically

## 🖥️ Running the Application

```bash
streamlit run app.py
```

## 💡 Usage

1. Open the Streamlit app in your browser
2. Use the chat input to ask legal questions
3. Explore retrieved legal information
4. Download summaries and review query history

## 🔍 Query Examples

- "What are the steps to file a lawsuit in India?"
- "Explain the legal procedures for contract registration"
- "What are the key provisions in Indian corporate law?"

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/legal-research-assistant](https://github.com/yourusername/legal-research-assistant)

## 🙏 Acknowledgements

- [CrewAI](https://github.com/crewai/crewai)
- [Streamlit](https://streamlit.io/)
- [Google Gemini](https://cloud.google.com/vertex-ai/generative-ai)

---

**Disclaimer**: This tool is for informational purposes and should not be considered legal advice. Always consult with a qualified legal professional for specific legal guidance.

