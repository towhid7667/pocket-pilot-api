# Pocket Pilot

A FastAPI-based expense tracker with user authentication.

## Setup
1. clone the repository: `git clone`
2. Set up environment variables in `.env` (see `.env` example above)
3. Run with Docker: `make run`
4. Run tests: `make test`

## Features
- User registration/login with OTP verification via Gmail API.
- JWT-based authentication with Redis token blacklisting.
- SQLite database, RabbitMQ for async email tasks.
- Dockerized app, Celery worker, and tests.
- Flower: Monitor Celery tasks at `http://localhost/flower/`.
- Redoc: View API documentation at `http://localhost/redoc`.
- Nginx Proxy Manager: Web-based proxy management at `http://localhost:81`.
- Portainer: Manage Docker containers at `http://localhost:9000`.
- Telegram Notifications: Sends detailed error messages to your Telegram chat.

## Endpoints
- `POST /user/register`: Register a new user.
- `POST /user/verify`: Verify user with OTP.
- `POST /user/login`: Log in and get a JWT token.
- `POST /user/logout`: Log out and blacklist the token.
- `GET /user/{user_id}`: Get user info by ID (authenticated).
- `GET /user/`: Get all users (authenticated).
- `PUT /user/{user_id}`: Edit user details (name, profile picture, password; authenticated, own profile only).
- `POST /user/forgot-password`: Send a reset password OTP to the user's email.
- `POST /user/reset-password`: Verify OTP and reset the user's password.

## Docker Services
- **API**: `http://localhost` (via Nginx Proxy Manager)
- **Swagger UI**: `http://localhost/docs`
- **Redoc**: `http://localhost/redoc`
- **Flower**: `http://localhost/flower/`
- **RabbitMQ Management**: `http://localhost:15672` (username: `guest`, password: `guest`)
- **Nginx Proxy Manager**: `http://localhost:81` (admin UI)
- **Portainer**: `http://localhost:9000` (set up on first access)

## Nginx Proxy Manager Setup
1. Run `make run` to start the services.
2. Access `http://localhost:81`.
3. Log in with `NGINX_PROXY_MANAGER_ADMIN_EMAIL` and `NGINX_PROXY_MANAGER_ADMIN_PASSWORD` from `.env`.
4. Configure proxy hosts:
   - **API**: Host: `app`, Port: `8400`, Path: `/`.
   - **Flower**: Host: `flower`, Port: `5555`, Path: `/flower/`.
   - **Docs**: Host: `app`, Port: `8400`, Path: `/docs`.
   - **Redoc**: Host: `app`, Port: `8400`, Path: `/redoc`.