# Deployment to a local host

1) Install the required Python packages in requirements.txt
2) Run the following commands inside of 2nd `QRLogin` directory
```python
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser
```
3) Follow the prompts to create an admin account. Currently this is the only method for creating an account on the managment site, as the actual account creation process would heavily depend on how the service is setup. For example, do we require an e-mail to login, or do we allow methods such as "Sign In With Google", using a phone number to signin, etc. Since the purpose of this project is to demonstrate two-factor authentication, and not to demonstrate how to sign-up to a webiste, using Djangos bultin `createsuperuser` command is acceptable. 
4) To run the demonstrations site on localhost (127.0.0.2:8000) use
```python
py manage.py runserver 127.0.0.2:8000
```
We are running it on 127.0.0.2 instead of 127.0.0.1 because that IP is being used for the demonstration site. 

