# STANGIAPP
### Django backend for a reminders' management applicationi, and related ReactJS frontend, with:
- Nginx reverse proxy with automatic keys update
- Manager dashboard for creation and managements of user profiles and reminders
- API with secure authentication through access token, refresh token and csrf token
- (Truly) dynamic user profiles
- Upload/Download services with Seafile server sinchronization and dedicated repositories
- Asinchronous email notifications through celery
- ReactJS mobile web application

### Create a production environment
- Register a domain
- Set up a Seafile server
- Create .env.prod, .env.prod.db and .env.prod.proxy-companion from samples, basing on your needs
- Run "docker-compose -f docker-compose.prod.yml --build -d" to build and start the dockers
- Run "docker-compose makemigrations && docker-compose migrate && docker-compose collectstatic" to generate databases and default Django static files
- Run "docker-compose createsuperuser" to create a default platform administrator
- Run "cd frontend && npm run relocate" to build your app and publish the related static blob

### Urls:
- https://example.com/ (TODO: Homepage)
- https://example.com/admin (Django administrator console)
- https://example.com/manager/login/ (Manager console)
- https://example.com/api/ (exposed services)
- https://example.com/login (Mobile web app login)
