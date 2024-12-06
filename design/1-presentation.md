# 🚀 AI-Powered Resume Builder
## Automated Resume & Cover Letter Generation System

**Author:** Muja Kayadan
**ID:** 616196

---

## 🎯 Problem Statement

Job seekers face challenges in:
- Creating tailored resumes for each application
- Maintaining consistency across applications
- Formatting documents professionally
- Writing compelling cover letters
- Managing multiple versions of documents

Our solution automates and streamlines this entire process using AI.

---

## 📋 Requirement Analysis

### Functional Requirements
1. **Resume Generation**
   - AI-powered content customization
   - Multiple section support
   - PDF generation
   - Template selection

2. **Cover Letter Creation**
   - Job-specific customization
   - Company research integration
   - Professional formatting

3. **Document Management**
   - Version control
   - PDF storage
   - Content versioning
   - Application tracking

4. **User Management**
   - Authentication
   - Profile management
   - Portfolio storage

### Non-Functional Requirements
1. **Performance**
   - Resume generation < 2 minutes
   - PDF compilation < 30 seconds
   - API response time < 500ms

2. **Security**
   - Encrypted data storage
   - Secure API endpoints
   - Token-based authentication

3. **Scalability**
   - Support multiple AI models
   - Handle concurrent users
   - Efficient database operations

---

## 🏗️ Architecture

### System Architecture

### Key Technologies
- 🤖 **AI Models**
  - **[OpenAI GPT-4](https://openai.com)** ![OpenAI](https://shields.io/badge/OpenAI-412991?logo=openai&style=flat)
    - State-of-the-art language model
    - Advanced reasoning capabilities
    - Context-aware responses
    - Temperature control for creativity

  - **[Anthropic Claude](https://anthropic.com)** ![Anthropic](https://shields.io/badge/Claude-6B47ED?style=flat)
    - Constitutional AI model
    - Strong at technical tasks
    - Long context window
    - Structured output

  - **[Google Gemini](https://deepmind.google/technologies/gemini/)** ![Google](https://shields.io/badge/Gemini-4285F4?logo=google&style=flat)
    - Multimodal capabilities
    - Fast processing
    - Advanced reasoning
    - Code understanding

  - **[Ollama](https://ollama.ai/)** ![Ollama](https://shields.io/badge/Ollama-000000?style=flat)
    - Local AI model hosting
    - Privacy-focused processing
    - No API costs
    - Supported Models:
      - Llama 3.1 (7B, 13B)
      - Mistral (7B)
      - CodeLlama
      - Phi-2
      - Neural Chat
    - Benefits:
      - Offline operation
      - Full control over models
      - Customizable parameters
      - Lower latency

- 📄 **Document Processing**
  - [LaTeX](https://www.latex-project.org/) - Professional document formatting
  - [PyPDF2](https://pypdf2.readthedocs.io/) - PDF manipulation

- 🔧 **Backend**
  - [FastAPI](https://fastapi.tiangolo.com/) - Modern API framework
  - [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
  - [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

---

## 📊 Database Design

The ER diagram shows our data structure:

Key entities:
- User (manages authentication and profiles)
- Portfolio (stores user's professional information)
- Resume (tracks generated documents)
- Preamble (manages LaTeX templates)

---

### Core Technologies & Libraries

#### 🖥️ Frontend
- **[Streamlit](https://streamlit.io/)** ![Streamlit](https://shields.io/badge/streamlit-FF4B4B?logo=streamlit&style=flat)
  - Rapid UI development
  - Real-time updates
  - Interactive components
  - Session state management

#### 📄 Document Processing
- **[LaTeX](https://www.latex-project.org/)** ![LaTeX](https://shields.io/badge/LaTeX-008080?logo=latex&style=flat)
  - Custom document classes
  - Professional typography
  - Template system
  - PDF generation

#### 🤖 AI & ML
- **[OpenAI](https://openai.com)** ![OpenAI](https://shields.io/badge/OpenAI-412991?logo=openai&style=flat)
  - GPT-4 for content generation
  - API integration
  - Temperature control
- **[Anthropic Claude](https://anthropic.com)** 
  - Alternative AI model
  - Constitutional AI
- **[Google Gemini](https://deepmind.google/technologies/gemini/)** ![Google](https://shields.io/badge/Gemini-4285F4?logo=google&style=flat)
  - Multimodal capabilities
  - Fast processing
- **[Ollama](https://ollama.ai/)** ![Ollama](https://shields.io/badge/Ollama-000000?style=flat)
  - Local AI model hosting
  - Multiple model support (Llama, Mistral, etc.)
  - No API costs
  - Privacy-focused processing

#### 🔧 Backend Framework
- **[FastAPI](https://fastapi.tiangolo.com/)** ![FastAPI](https://shields.io/badge/FastAPI-009688?logo=fastapi&style=flat)
  - Modern API framework
  - Async support
  - OpenAPI documentation
  - Type validation

#### 🗄️ Database
- **[MongoDB](https://www.mongodb.com/)** ![MongoDB](https://shields.io/badge/MongoDB-47A248?logo=mongodb&style=flat)
  - Document storage
  - Portfolio management
  - Resume tracking
- **[SQLAlchemy](https://www.sqlalchemy.org/)** ![SQLAlchemy](https://shields.io/badge/SQLAlchemy-CC2927?style=flat)
  - ORM functionality
  - Database abstraction

#### 📚 Key Python Libraries
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** ![Pydantic](https://shields.io/badge/Pydantic-E92063?style=flat)
  - Data validation
  - Settings management
- **[PyPDF2](https://pypdf2.readthedocs.io/)** ![PyPDF2](https://shields.io/badge/PyPDF2-000000?style=flat)
  - PDF manipulation
  - Document merging
- **[python-jose](https://python-jose.readthedocs.io/)** ![JWT](https://shields.io/badge/JWT-000000?logo=jsonwebtokens&style=flat)
  - JWT authentication
  - Token management

#### 🔍 Testing & Quality
- **[Pytest](https://pytest.org/)** ![Pytest](https://shields.io/badge/Pytest-0A9EDC?logo=pytest&style=flat)
  - Unit testing
  - Integration testing
  - Coverage reporting
- **[Black](https://black.readthedocs.io/)** ![Black](https://shields.io/badge/Black-000000?style=flat)
  - Code formatting
- **[Flake8](https://flake8.pycqa.org/)** ![Flake8](https://shields.io/badge/Flake8-3776AB?style=flat)
  - Code linting

### System Components

1. **Streamlit UI**
   - Real-time preview
   - Section management
   - Model selection
   - Template customization

2. **LaTeX System**
   - Custom document classes
   - Professional templates
   - Dynamic content insertion
   - PDF compilation

3. **AI Integration**
   - Multiple model support
   - Content generation
   - Section optimization
   - Job matching

4. **Database System**
   - Portfolio management
   - Version control
   - Document storage
   - User preferences