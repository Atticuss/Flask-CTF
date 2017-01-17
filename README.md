# Flask-CTF
Quick and dirty Flask app for large class CTFs. DB conn info stored within the ctf.conf file.

## OSX ##
brew unlink freetds; brew install homebrew/versions/freetds091

pip3 install pymssql, Flask

python3 ctf.py --build-db

python3 ctf.py
