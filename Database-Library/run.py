import pymysql
pymysql.install_as_MySQLdb()
from librarydb import app

if(__name__ == "__main__"):
    app.run(debug = True, host = "localhost", port = 3000)
