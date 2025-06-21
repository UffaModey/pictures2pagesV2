# 📸 pictures2pagesV2

Turn uploaded images into AI-generated poems and stories using this full-stack, cloud-native backend API. Powered by Python, FastAPI, and AWS, this project gives users the ability to log in, upload images, create content from them, and control the visibility of their creations.

## 🚀 Features

- ✅ User registration and authentication with PyJWT
- 📸 Upload to S3 and manage images 
- ✍️ Generate poems or stories from images using OpenAI
- 🔒 Set content visibility (public or private)
- 🔍 Browse public content by other users
- 🗑️ Delete any of your content
- 🐳 Run locally with Docker
- ☁️ Deploy using AWS Lambda, API Gateway, S3, and RDS
- 📑 API documentation via Swagger
- 🧪 Tested endpoints and CI/CD ready

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI (Python)
- **AI Integration**: OpenAI API
- **Database**: PostgreSQL
- **Authentication**: AWS Cognito (OAuth2 & JWT)
- **Cloud Services**: AWS Lambda, S3, RDS, API Gateway
- **Containerization**: Docker
- **CI/CD & Git**: GitHub Actions
- **API Docs**: Swagger/OpenAPI

## 📦 Setup (Local Development)

1. Clone the repo:
    ```bash
    git clone https://github.com/yourusername/image2imagination.git
    cd image2imagination
    ```

2. Run with Docker:
    ```bash
    docker-compose up --build
    ```

3. Visit:
    - `http://localhost:8000/docs` to see the API docs (Swagger)

## ✍️ API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Create a new user |
| POST | `/login` | Log in user |
| DELETE | `/user/{id}` | Delete user |
| GET | `/user/{id}` | Get user details + public content |
| POST | `/upload/image` | Upload image |
| POST | `/generate/poem` | Generate poem from image |
| POST | `/generate/story` | Generate story from image |
| PATCH | `/content/{id}/visibility` | Set content as public/private |
| DELETE | `/content/{id}` | Delete image, poem, or story |

## 📄 License

GNU License
