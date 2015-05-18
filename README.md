# cproj
Produce a Coxeter projection diagram

## Requirements
* Python libraries
  * flask
  * mpld3
  * mpldatacursor
* Apache setup
  * http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
  * ```libapache2-mod-wsgi```
  * create ```*.wsgi```
  * configure Apache
    * edit ```/etc/apache2/sites-available/*.conf```
    * ```sudo service apache2 restart```
