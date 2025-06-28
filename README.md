# ilab-test

# intruduction
    ilab-test is a ai chat bot with secure login

# installed libraries 
    - fastapi
    - sqlalchemy
    - python-jose[cryptography]
    - passlib[bcrypt]
    - python-multipart

# instructions
please install above libraries then run using

    - config api keys in env
    - do not change ALGORITHM value

cmd =>
    - fastapi dev main.py
    - uvicorn main:app --reload 

Then create users using 
http://127.0.0.1:8000/docs

To assess user specific please authenticate