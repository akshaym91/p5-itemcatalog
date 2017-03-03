# Missiley
Udacity Fullstack Web Developer Project 5: A Country-Missile Catalog

This project is built with Python backend with:
- Flask as the web framework to expose APIs
- Spectre.css as the CSS framework for the look and feel
- OAuth implementation using GPlus and Facebook
- CRUD operations into an SQLLite Database
- SQL Alchemy as an ORM

##Public URL
The project is yet to be hosted on cloud.

##How to Use?
1. Unpack the zip into a folder or clone the repo.
2. Using the VagrantFile attached, start a VM.
```
vagrant up
```
SSH into the machine as `vagrant` user
```
vagrant ssh
```
3. Place the rest of the contents (other than the VagrantFile) in the /vagrant folder and move to that folder.
```
cd /vagrant/catalog
```
4. Setup the Database by running:
```
python databsae_setup.py
```
5. To initialiaze the databse with some values:
```
python lots_of_missiles.py
```
4. At the root level, run
```
python app.py
```

##Author
Akshay Menon

##License
MIT

##Copyright
Copyright &copy; 2016 Akshay Menon
