# cproj
Produce a Coxeter projection diagram

## Requirements
* Python libraries
  * flask
  * mpld3
  * mpldatacursor
* SAGE
* Apache setup
  * http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
  * ```libapache2-mod-wsgi```
  * create ```*.wsgi```
  * configure Apache
    * edit ```/etc/apache2/sites-available/*.conf```
    * ```a2ensite/a2dissite <site_config_filename>```
    * ```sudo service apache2 restart```
