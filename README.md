# TITLE
## Database Systems coursework
Joe Halloran

## Exectuive summary

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

<div style="page-break-after: always;"></div>

## iIntroduction

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Task 1 & 2: Database set up and data upload

The data we are handling is historical, and therefore very unlikely to be altered (unless of course some new data was discovered in a dusty filing cabinet in a rarely visited hospital wing). Therefore we can treat the data as effectively static.

With this in mind, I wanted to create an isolated and automated (where possible) means of setting up the database, so it could be easily rebuilt if problems were discovered in the configuration.

A full description of the process, including scripts written is included as an appendix. In addition, you can find a summary of the process below.

For the reasons outlined above (isolated, replicable, and automated). I created a virtual server using Vagrant *(Vagrant by Hashicorp (2017))* running Ubuntu 14.04 server addition *Ubuntu 14.04.5 LTS (2017)*. I then set up a LAMP server *(LAMP (software bundle) - Wikipedia (2017))*, created an Apache web server and installed phpmyadmin *(How to install phpmyadmin on ubuntu - Liquid Web (2017))*.

I then wanted to create a script that would set up the database and populate the tables with data from the spreadsheet files provided for the task. I decided to use the Python SQL Alchemy module *(SQL Alchemy - The Database Toolkit for Python (2017))*, which provides an ORM. This is a useful means of  visualising the database by creating tables as Python classes.

I created two scripts `database_setup.py` (creates tables) and `populate_db.py` (parses csv files and uploads to databases). This allowed me to search for and eliminate duplicates (for instance in the two files that list all registered gp surgeries, the files where >99% duplicate).

The one great drawback of this approach was the time it took to run the `populate_db.py` script. It took over 8 hours!! to complete the process of populating the tables with data. This is for a number of reasons:
1. The sheer scale of the data: two of the csv files where 1.4GB.
2. Limited hardware resources made available to the virtual mysql server: for instance, it had access to only 512MB of ram on the host machine.
3. The extra cost of using an ORM tool: SQL Alchemy added an extra layer of complexity.
4. Some data integrity vs speed trade-offs in the `populate_db.py` code: For instance, the `session.commit()` command, which commits changes to the database, is run after every line in the csv file is parsed. This could have been run only at the end of the file, or after *x* lines are parsed, to reduce the number of commits and therefore execution time. However, this would create a risk of data loss if the program terminated before reaching the end of the file or *x* lines.

Despite this huge time delay, these files provided a reliable, automated, and replicable means of creating the databases.

## questions

a) How many practices and registered patients are there in the N17 postcode Area?
http://releases.ubuntu.com/14.04/
SELECT COUNT(postcode) from surgery where postcode like "n17%"
+-----------------+
| COUNT(postcode) |
+-----------------+
|               7 |
+-----------------+
1 row in set (0.01 sec)


select sum(totalAll) from surgery_data where postcode LIKE "N17%";
+---------------+
| sum(totalAll) |
+---------------+http://releases.ubuntu.com/14.04/
|         52248 |
+---------------+
1 row in set (0.01 sec)


> Note discrepancy in practice IDs in tables

select totalAll, practice from surgery_data where
practice = "F85017" or
practice = "F85019" or
practice = "F85028" or
practice = "F85030" or
practice = "F85615" or
practice = "F85628" or
practice = "Y04848";


http://releases.ubuntu.com/14.04/
b) Which practice prescribed the most beta blockers per registered patients in total over the two month period?

http://www.nhs.uk/conditions/beta-blockers/pages/introduction.aspx

select practice, sum(items) as "beta-blockers" from treatment where
bnf_name like "%atenolol%" or
bnf_name like "%Tenormin%" or
bnf_name like "%bisoprolol%" or
bnf_name like "%Cardicor%" or
bnf_name like "%Emcor%" orhttp://releases.ubuntu.com/14.04/
bnf_name like "%carvedilol%" or
bnf_name like "%toprolol%" or
bnf_name like "%Betaloc%" or
bnf_name like "%Lopresor%" or
bnf_name like "%nebivolol%" or
bnf_name like "%Nebilet%" or
bnf_name like "%Inderal%"
group by practice
limit 10;

c) Which was the most prescribed medication across all practices?

select treatment.bnf_code from treatment
left join chemical on chemical.chem_sub_code = LEFT(treatment.bnf_code, 9);

d) Which practice spent the most and the least per patient?

select practice, round(sum(act_cost),2) as total from treatment group by practice order by sum(act_cost) desc limit 1;
+----------+------------+
| practice | total      |
+----------+------------+
| M85063   | 1638640.13 |
+----------+------------+
1 row in set (16.98 sec)

select treatment.practice, round(sum(treatment.act_cost),2) as total, surgery_data.totalAll from treatment inner join surgery_data on treatment.practice = surgery_data.practice group by treatment.practice order by total desc limit 1;



e) What was the difference in selective serotonin reuptake inhibitor prescriptions between January and February?

select period, count(bnf_name) as selective serotine from treatment where bnf_name like "%serotonin reuptake inhibitor%" group_by period;

f) Visualise the top 10 practices by number of metformin prescriptions throughout the entire period.

select count(bnf_name) from treatment where bnf_name like "%metaformin%";
select bnf_name from treatment where bnf_name like "%metformin%" group by practice;

## Task 4: Observations of Database

- Different postcodes in two databases in task 1

# Refs

https://stackoverflow.com/questions/29355674/how-to-connect-mysql-database-using-pythonsqlalchemy-remotely
https://stackoverflow.com/questions/12748926/sqlalchemy-check-if-object-is-already-present-in-table
https://stackoverflow.com/questions/2594829/finding-duplicate-values-in-a-sql-table


## Bibliograph

* Vagrant by Hashicorp (2017). Available at:<br />
https://www.vagrantup.com/ (Accessed: 13th June 2017).

* Ubuntu 14.04.5 LTS (2017). Available at:<br />
http://releases.ubuntu.com/14.04/ (Accessed: 13th June 2017)

* LAMP (software bundle) - Wikipedia (2017). Available at:<br />
https://en.wikipedia.org/wiki/LAMP_ (Accessed: 13th June 2017)

* How to install phpmyadmin on ubuntu - Liquid Web (2017). Available at:<br />
https://www.liquidweb.com/kb/how-to-install-and-configure-phpmyadmin-on-ubuntu-14-04/ (Accessed: 13th June 2017)

* Welcome! - The Apache HTTP Server Project (2017). Available at:<br />
https://httpd.apache.org/ (Accessed: 13th June 2017)

* SQL Alchemy - The Database Toolkit for Python (2017). Available at:<br />
https://www.sqlalchemy.org/ (Accessed: 13th June 2017)


# Set up

Vagrant PHP and Mysql

Php my admin
sudo apt-get install phpmyadmin php-mbstring php-gettext
sudo nano apache2.conf

PIP
sudo apt-get install python-dev python-pip python-setuptools build-essential


PIP install pymysql

$ mysql -u root -p

mysql> create database PrescriptionsDB;

## Upload REPORT
vagrant@vagrant-ubuntu-trusty-64:/vagrant$ python populate_db.py
BEGIN EXECUTION AT: Sun, 11 Jun 2017 07:29:17 +0000

('UPLOAD REPORT:', 'T201601CHEMSUBS.CSV')
('Lines parsed: ', 3432)
('Errors: ', 0)
('Duplicates: ', 0)

('UPLOAD REPORT:', 'T201602CHEMSUBS.CSV')
('Lines parsed: ', 3433)
('Errors: ', 0)
('Duplicates: ', 3432)

('UPLOAD REPORT:', 'T201601ADDRBNFT.CSV')
('Lines parsed: ', 9905)
('Errors: ', 0)
('Duplicates: ', 0)

('UPLOAD REPORT:', 'T201602ADDRBNFT.CSV')
('Lines parsed: ', 9916)
('Errors: ', 0)
('Duplicates: ', 9753)

('UPLOAD REPORT:', 'gp-reg-patients-prac-quin-age.csv')
('Lines parsed: ', 7712)
('Errors: ', 0)
('Duplicates: ', 0)
BEGIN LARGE FILE 1: Sun, 11 Jun 2017 07:30:46 +0000

('UPLOAD REPORT:', 'T201601PDPIBNFT.CSV')
('Lines parsed: ', 10036406)
('Errors: ', 0)
('Duplicates: ', 0)
BEGIN LARGE FILE 1: Sun, 11 Jun 2017 12:00:56 +0000

('UPLOAD REPORT:', 'T201602PDPIBNFT.CSV')
('Lines parsed: ', 10037913)
('Errors: ', 0)
('Duplicates: ', 0)
COMPLETED: Sun, 11 Jun 2017 15:51:15 +0000
