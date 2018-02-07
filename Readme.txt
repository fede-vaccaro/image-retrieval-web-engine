Needed package:

numpy;
tensorflow(<1.5);
keras; 
django;
django_restframework;
pillow;
h5py;

copy "populate_db.py" to ~/lib/site-packages/django/core/managament/commands/

I suggest to create a virtualenv.
1) python manage.py makemigrations (this is supposed to doesn't be needed but do it the same) 
2) python manage.py migrate (to create the tables)

after copy the populate_db file where specified above, put your image dataset (only .jpg supported for now) in image-retrieval-web-engine/img/ 

3) python manage.py populate_db

Try it in 127.0.0.1:8000 by 

4) python manage.py runserver
