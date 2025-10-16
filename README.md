# News Content Aggregator & Summarizer

A full-stack application that aggregates content from multiple sources and generates AI-powered summaries.

## 🚀 Features

- **Multi-source Aggregation**: Fetches content from Reddit, News APIs, and RSS feeds
- **AI Summarization**: Uses LLMs to generate concise article summaries
- **Modern Stack**: FastAPI backend + Next.js frontend with TypeScript
- **Cloud Native**: Containerized with Docker and ready for deployment

## 🏗️ Architecture

```bash
app-news-aggregator/
├── backend/ # FastAPI Python application
├── frontend/ # Next.js TypeScript application
├── docs/ # Documentation
└── README.md
````


## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Hugging Face/Groq** - AI summarization

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload