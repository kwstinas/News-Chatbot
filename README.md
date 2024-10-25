This repository contains a News Chatbot Web Application that allows users to interact with current news articles through a conversational interface. Designed to make news exploration intuitive and engaging, the application consists of a FastAPI backend with a MongoDB database, and a React-based frontend. Powered by Llama-2, the chatbot enables users to ask questions, get summaries, and receive filtered news on demand.

Features
1. Full-Stack Web Application
This application provides a complete, responsive web-based solution where users can interact with news data through a chatbot, available from any web browser.

Frontend: Built with HTML, CSS, and React, the frontend presents a user-friendly interface where users can engage with the chatbot and view responses dynamically.
Backend: The FastAPI-based backend manages data flow between MongoDB and the chatbot interface, ensuring smooth communication and data retrieval.
2. Chatbot Interface Powered by Llama-2
The chatbot is powered by Llama-2, enabling natural language understanding and interaction with stored news data. Through the chatbot, users can:

Ask questions about recent events, specific topics, or articles by a particular author.
Request summaries or detailed explanations of news stories.
Filter results based on criteria like publication date, topic, or location.
3. MongoDB News Database
The backend stores news articles in MongoDB, enabling scalable data storage and efficient retrieval. PyMongo connects the backend to MongoDB, and data is automatically populated through web scraping scripts to ensure the database remains current.

4. Real-Time News Data Collection
Articles are collected from various news sources using automated web scraping, which updates the MongoDB database in real-time. The application ensures that the chatbot always has access to the latest information.

Technology Stack
Frontend: React, HTML, CSS, Axios (for API requests)
Backend: FastAPI, MongoDB (with PyMongo)
Chatbot: Llama-2 conversational AI model
ASGI Server: Uvicorn
Project Structure
frontend/: Contains the React-based frontend code, with components for the chatbot UI, styling, and API integration.
backend/: Houses the FastAPI code for serving the API, handling MongoDB interactions, and facilitating the chatbot’s backend logic.
scraping/: Scripts for collecting articles from news websites and populating MongoDB with fresh content.
