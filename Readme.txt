
## to-do
- make _post.html responsive for phones by replacing table with divs
- do same with user_profile.html
- see astha's posts for more todos

################____Install Notes____#################
# virtual environment for this project
virtualenvironment is not added to git, create one where you clone this project.
In this repo, the virtual environment folder is already added to .gitignore file so to carry on this legacy of not including virtualenvironment in git repo,
just name your new virtualenvironment as "pehla_virtualenv" as this folder name is already added to .gitignore

to make a virtualenvironment use command : python -m venv <virtual_env_name>
then to install all dependencies : 
1) activate your venv
2) pip install -r requirements.txt

# requirements.txt file
requirements.txt is added/updated using : pip freeze > requirements.txt
ALWAYS UPDATE requirements.txt WHENEVER YOU COMMIT, ALWAYS.

# database migrations
do database migrations whenever you update db schema
using commands :
-> flask db migrate -m "migration message"
-> flask db upgrade

# To add any file/folder to .gitignore 
-> echo file_or_folder_name >> .gitignore
note : 
if the file/folder has been tracked or commited to the git repo before adding it to the .gitignore,
then it needs to be removed from repo, using the below command:
-> git rm --cached -r <filename>


# about database
this project uses SQLAlchemy orm, can be configured for any sql database.
currently configured for using mysql server, earlier was using sqlite - hence the app.db file in repo
to change db uri or db altogether, see config.py and the "SQLALCHEMY_DATABASE_URI" variable in it.

