# MeetEZ – Smart Event Coordination Platform

**MeetEZ** is a cloud-hosted event coordination platform designed to streamline the process of organizing, managing, and attending events. Built with Python Flask, Dash, and PostgreSQL, it offers dynamic interfaces for event creation, user subscriptions, and real-time notifications. The application is deployed on Azure with continuous integration and secure secret management through Azure Key Vault.

## Live Deployment

The application is hosted on **Azure App Service**, with automated deployment managed through **GitHub Actions**.  
Access it here:  
(No longer accessible because its expensive to leave running)

## Features

- Create and manage public events  
- Subscribe and unsubscribe from events  
- View attendee lists for each event  
- Email notifications sent automatically via SendGrid when events are updated  
- PostgreSQL backend for persistent storage  
- Dash-powered UI with modular layout and navigation  

## Technology Stack

| Component        | Technology                      |
|------------------|----------------------------------|
| Backend          | Python (Flask)                  |
| Frontend / UI    | Dash by Plotly                  |
| Database         | PostgreSQL                      |
| Email Service    | SendGrid (via Twilio)           |
| Hosting          | Azure App Service               |
| CI/CD            | GitHub Actions                  |
| Secret Storage   | Azure Key Vault                 |

## Design & Architecture

MeetEZ applies several design principles and patterns for maintainability and scalability:

- **Adapter Pattern**: Abstracts database connectivity for flexibility across environments  
- **Observer Pattern**: Manages email notifications to users on event changes  
- **Singleton Pattern**: Controls core service instances (e.g., database connector)  
- Architectural documentation follows the **4+1 View Model** approach  
