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

With this in mind and safe in the knowledge we do not need to worry about additions to the data, I wanted to create an isolated and automated (where possible) means of setting up the database, so it could be easily rebuilt if problems were discovered in the configuration.

A full description of the process, including scripts written is included as an appendix. In addition, you can find a summary of the process below.

For the reasons outlined above (isolated, replicable, and automated). I created a virtual server using Vagrant *(Vagrant by Hashicorp (2017))* running Ubuntu 14.04 server addition *Ubuntu 14.04.5 LTS (2017)*. I then set up a LAMP server *(LAMP (software bundle) - Wikipedia (2017))* and installed phpmyadmin *(How to install phpmyadmin on ubuntu - Liquid Web (2017))* to give me GUI access to the DB.

I then wanted to create a script that would set up the database and populate the tables with data from the spreadsheet files provided for the task. I decided to use the Python SQL Alchemy module *(SQL Alchemy - The Database Toolkit for Python (2017))*, which provides an ORM. This is a useful means of  visualising the database by creating tables as Python classes.

I created two scripts `database_setup.py` (creates tables) and `populate_db.py` (parses csv files and uploads to databases). This allowed me to search for and eliminate duplicates (for instance in the two files that list all registered gp surgeries, were >99% duplicated).

The one great drawback of this approach was the time it took to run the `populate_db.py` script. It took over 8 hours!! to complete the process of populating the tables with data. This is for a number of reasons:
1. The sheer scale of the data: two of the csv files where 1.4GB.
2. Limited hardware resources made available to the virtual mysql server: for instance, it had access to only 512MB of ram on the host machine.
3. The extra cost of using an ORM tool: SQL Alchemy added an extra layer of abstraction.
4. Some data integrity vs speed trade-offs in the `populate_db.py` code: For instance, the `session.commit()` command, which commits changes to the database, is run after every line in the csv file is parsed. This could have been run only at the end of the file, or after *x* lines are parsed, to reduce the number of commits and therefore execution time. However, this would create a risk of data loss if the program terminated before reaching the end of the file or *x* lines.

Despite this huge time delay, these process provided a reliable, mainly automated, and replicable means of creating the databases.

## Task 3: Database queries

## a) How many practices and registered patients are there in the N17 postcode Area?

There are 7 surgeries in the N17 area with 52248 patients

*Queries:*
```
SELECT COUNT(postcode) from surgery where postcode like "n17%"

+-----------------+
| COUNT(postcode) |
+-----------------+
|               7 |
+-----------------+
1 row in set (0.01 sec)
```

```
select sum(totalAll) from surgery_data where postcode LIKE "N17%";

+---------------+
| sum(totalAll) |
+---------------+
|         52248 |
+---------------+
1 row in set (0.01 sec)
```

## b) Which practice prescribed the most beta blockers per registered patients in total over the two month period?

This queries requires a definition of "beta-blockers", which was found here:
(Commonly use beta-blockers - NHS)[http://www.nhs.uk/conditions/beta-blockers/pages/introduction.aspx]

The term "prescribed the most" also requires some consideration. If we are counting the number of times a beta-blockers was prescribed we would have to look at the 'items' column. If we were looking at the sheer amount of drugs that was given to patients, we should look at 'quantity'. My gut instinct lead me to look at the number of prescriptions and therefore focus on a sum of 'items'.

I also decided to return the top 10 practices, to see if the top item is an outlier.

```
select
treatment.practice as "GP id",
sum(treatment.items) as "Total beta-blockers",
surgery_data.totalAll as "total patients",
(sum(treatment.items)/surgery_data.totalAll) as "Average"
from surgery_data
inner join treatment on treatment.practice = surgery_data.practice
where
bnf_name like "%atenolol%" or
bnf_name like "%Tenormin%" or
bnf_name like "%bisoprolol%" or
bnf_name like "%Cardicor%" or
bnf_name like "%Emcor%" or
bnf_name like "%carvedilol%" or
bnf_name like "%toprolol%" or
bnf_name like "%Betaloc%" or
bnf_name like "%Lopresor%" or
bnf_name like "%nebivolol%" or
bnf_name like "%Nebilet%" or
bnf_name like "%Inderal%"
group by treatment.practice
order by Average desc
limit 10;

+--------+---------------------+----------------+---------+
| GP id  | Total beta-blockers | total patients | Average |
+--------+---------------------+----------------+---------+
| G82651 |                  12 |              1 | 12.0000 |
| Y04786 |                 609 |            316 |  1.9272 |
| B86674 |                  12 |             20 |  0.6000 |
| E87711 |                 167 |            284 |  0.5880 |
| Y02511 |                 339 |            710 |  0.4775 |
| B81683 |                 662 |           1727 |  0.3833 |
| A89040 |                1002 |           2902 |  0.3453 |
| Y02625 |                 378 |           1095 |  0.3452 |
| C88626 |                 538 |           1599 |  0.3365 |
| Y00081 |                  12 |             37 |  0.3243 |
+--------+---------------------+----------------+---------+
10 rows in set (2 min 8.14 sec)
```

As suspected the top item is a bit of anomaly, with only one patient. Further investigate revealed G82651 is a private nursing *(Burrswood nursing home (2017))* home that accepts a small number of NHS patients, this explains the one patient.

```
select gp_id, name, postcode from surgery where gp_id = "G82651";
+--------+------------------------+----------+
| gp_id  | name                   | postcode |
+--------+------------------------+----------+
| G82651 | BURRSWOOD NURSING HOME | TN3 9PY  |
+--------+------------------------+----------+
1 row in set (0.00 sec)
```


## c) Which was the most prescribed medication across all practices?

As with question b, the term "most prescribed" requires technical definition. For consistency, I stuck with summing values in the 'item' columns.

The term "prescribed medication" also requires unpicking. I first grouped by "bnf_code".

```
select bnf_code, bnf_name, sum(items) as total from treatment group by bnf_code order by total desc limit 1;
+-----------------+-------------------------+---------+
| bnf_code        | bnf_name                | total   |
+-----------------+-------------------------+---------+
| 0103050P0AAAAAA | Omeprazole_Cap E/C 20mg | 4269629 |
+-----------------+-------------------------+---------+

1 row in set (26.55 sec)
```

However a BNF code describes a particalur drug at particular dosage and in a particalur form. This seemed too narrow, as the same drug, when prescribed in different forms and at quantities, is counted separately.

For this reason, and after looking the Chemical table, I decided the look at the first 9 characters of the bnf code. This appears to be a base code for drugs of the same type. This gave me a final result of:

> Unique shortened bnf_code (based from chemicals)

```
select left(bnf_code,9) as sub_code, bnf_name, sum(items) as total from treatment group by sub_code order by total desc limit 1;

+-----------+----------------------+---------+
| sub_code  | bnf_name             | total   |
+-----------+----------------------+---------+
| 0212000Y0 | Simvastatin_Tab 40mg | 5116027 |
+-----------+----------------------+---------+
```

Digging a little further, I found that this drug came in a variety of names and quantities:

```
select left(bnf_code,9) as sub_code, bnf_name, count(items) from treatment where left(bnf_code,9) = "0212000Y0" group by bnf_name;

+-----------+------------------------------------+--------------+
| sub_code  | bnf_name                           | count(items) |
+-----------+------------------------------------+--------------+
| 0212000Y0 | Simvador_Tab 10mg                  |          409 |
| 0212000Y0 | Simvador_Tab 20mg                  |          757 |
| 0212000Y0 | Simvador_Tab 40mg                  |         1020 |
| 0212000Y0 | Simvador_Tab 80mg                  |           70 |
| 0212000Y0 | Simvastatin_Liq Spec 40mg/5ml      |            1 |
| 0212000Y0 | Simvastatin_Oral Susp 20mg/5ml S/F |          631 |
| 0212000Y0 | Simvastatin_Oral Susp 40mg/5ml S/F |          946 |
| 0212000Y0 | Simvastatin_Tab 10mg               |        14733 |
| 0212000Y0 | Simvastatin_Tab 20mg               |        15650 |
| 0212000Y0 | Simvastatin_Tab 40mg               |        15697 |
| 0212000Y0 | Simvastatin_Tab 80mg               |        10203 |
| 0212000Y0 | Zocor_Tab 10mg                     |          301 |
| 0212000Y0 | Zocor_Tab 20mg                     |          534 |
| 0212000Y0 | Zocor_Tab 40mg                     |          452 |
| 0212000Y0 | Zocor_Tab 80mg                     |           38 |
+-----------+------------------------------------+--------------+
15 rows in set (12.65 sec)
```

## d) Which practice spent the most and the least per patient?

```
select practice, round(sum(act_cost),2) as total from treatment group by practice order by sum(act_cost) desc limit 1;
+----------+------------+
| practice | total      |
+----------+------------+
| M85063   | 1638640.13 |
+----------+------------+
1 row in set (16.98 sec)

select treatment.practice, round(sum(treatment.act_cost),2) as total, surgery_data.totalAll from treatment inner join surgery_data on treatment.practice = surgery_data.practice group by treatment.practice order by total desc limit 1;
+----------+------------+----------+
| practice | total      | totalAll |
+----------+------------+----------+
| M85063   | 1638640.13 |    60352 |
+----------+------------+----------+
1 row in set (1 hour 40 min 41.92 sec)

select sum(treatment.act_cost) as total, surgery_data.totalAll, (sum(treatment.act_cost)/surgery_data.totalAll) as "Average" from surgery_data inner join treatment on treatment.practice = surgery_data.practice where treatment.practice = "M85063";
+--------------------+----------+--------------------+
| total              | totalAll | Average            |
+--------------------+----------+--------------------+
| 1638640.1302093118 |    60352 | 27.151380736501057 |
+--------------------+----------+--------------------+
1 row in set (11.63 sec)


select treatment.practice, sum(treatment.act_cost) as total, surgery_data.totalAll, (sum(treatment.act_cost)/surgery_data.totalAll) as "Average" from surgery_data inner join treatment on treatment.practice = surgery_data.practice group by treatment.practice order by Average limit 10;
+----------+--------------------+----------+----------------------+
| practice | total              | totalAll | Average              |
+----------+--------------------+----------+----------------------+
| Y01690   | 50.740000396966934 |     3777 | 0.013433942387335699 |
| N82647   |   33.8699996471405 |     1883 | 0.017987254193914233 |
| E87718   |  2.569999933242798 |       90 | 0.028555554813808864 |
| E87055   | 14.989999771118164 |      285 | 0.052596490424976015 |
| L85602   | 101.61999946832657 |     1499 |  0.06779186088614181 |
| M82612   |  277.7500001192093 |     2308 |  0.12034228774662448 |
| N81634   | 2728.3400220274925 |    13716 |  0.19891659536508402 |
| F84727   |  389.9899954199791 |     1847 |  0.21114780477529999 |
| Y02988   |  84.33999973535538 |      325 |  0.25950769149340114 |
| N85643   |  644.0400002002716 |     1779 |   0.3620236088815467 |
+----------+--------------------+----------+----------------------+
10 rows in set (1 hour 38 min 38.25 sec)

> Y01690 Only prescribed 2 items in Feb 2016
select sum(items), sum(act_c* ost), period from treatment where practice = "Y01690" group by period;
+------------+-------------------+--------+
| sum(items) | sum(act_cost)     | period |
+------------+-------------------+--------+
|         21 | 46.29000046849251 | 201601 |
|          2 | 4.449999928474426 | 201602 |
+------------+-------------------+--------+
2 rows in set (13.11 sec)

select gp_id, name, postcode from surgery where gp_id = "Y01690";
+--------+--------------------------+----------+
| gp_id  | name                     | postcode |
+--------+--------------------------+----------+
| Y01690 | SCHOOL LANE PMS PRACTICE | IP24 2AG |
+--------+--------------------------+----------+
1 row in set (0.01 sec)

> Only 1 patient

select treatment.practice, sum(treatment.act_cost) as total, surgery_data.totalAll, (sum(treatment.act_cost)/surgery_data.totalAll) as "Average" from surgery_data inner join treatment on treatment.practice = surgery_data.practice group by treatment.practice order by Average desc limit 10;
+----------+--------------------+----------+--------------------+
| practice | total              | totalAll | Average            |
+----------+--------------------+----------+--------------------+
| G82651   |  7609.050047278404 |        1 |  7609.050047278404 |
| Y02045   | 19572.239992558956 |        4 |  4893.059998139739 |
| Y01924   | 147981.80988019705 |      112 | 1321.2661596446164 |
| Y02873   | 10717.569992467761 |       20 |   535.878499623388 |
| Y02507   | 475.95999723672867 |        2 | 237.97999861836433 |
| Y02508   |  3333.070020824671 |       15 | 222.20466805497804 |
| Y04786   |  68229.09005251527 |      316 | 215.91484193833946 |
| Y02625   | 209576.74016997218 |     1095 | 191.39428326024856 |
| Y02511   |  131495.9803173244 |      710 |  185.2056060807386 |
| E87711   |  34552.28004068136 |      284 |  121.6629578897231 |
+----------+--------------------+----------+--------------------+
10 rows in set (1 hour 40 min 47.78 sec)

select gp_id, name, postcode from surgery where gp_id = "G82651";
+--------+------------------------+----------+
| gp_id  | name                   | postcode |
+--------+------------------------+----------+
| G82651 | BURRSWOOD NURSING HOME | TN3 9PY  |
+--------+------------------------+----------+
1 row in set (0.00 sec)
```


## e) What was the difference in selective serotonin reuptake inhibitor prescriptions between January and February?

http://www.nhs.uk/conditions/SSRIs-(selective-serotonin-reuptake-inhibitors)/Pages/Introduction.aspx
Types of SSRIs
There are currently seven SSRIs prescribed in the UK:
citalopram (Cipramil)
dapoxetine (Priligy)
escitalopram (Cipralex)
fluoxetine (Prozac or Oxactin)
fluvoxamine (Faverin)
paroxetine (Seroxat)
sertraline (Lustral)

```
select count(items) as "Serotonin prescriptions", period as selective_serotonin from treatment where
bnf_name like "%citalopram%" or
bnf_name like "%Cipramil%" or
bnf_name like "%dapoxetine%" or
bnf_name like "%Priligy%" or
bnf_name like "%escitalopram%" or
bnf_name like "%Cipralex%" or
bnf_name like "%fluoxetine%" or
bnf_name like "%Prozac%" or
bnf_name like "%Oxactin%" or
bnf_name like "%fluvoxamine%" or
bnf_name like "%Faverin%" or
bnf_name like "%paroxetine%" or
bnf_name like "%Seroxat%" or
bnf_name like "%sertraline%" or
bnf_name like "%Lustral%"
group by period;

+-------------------------+---------------------+
| Serotonin prescriptions | selective_serotonin |
+-------------------------+---------------------+
|                   99715 | 201601              |
|                   99215 | 201602              |
+-------------------------+---------------------+
2 rows in set (27.70 sec)

select sum(items) as "Serotonin prescriptions", period as selective_serotonin from treatment where
bnf_name like "%citalopram%" or
bnf_name like "%Cipramil%" or
bnf_name like "%dapoxetine%" or
bnf_name like "%Priligy%" or
bnf_name like "%escitalopram%" or
bnf_name like "%Cipralex%" or
bnf_name like "%fluoxetine%" or
bnf_name like "%Prozac%" or
bnf_name like "%Oxactin%" or
bnf_name like "%fluvoxamine%" or
bnf_name like "%Faverin%" or
bnf_name like "%paroxetine%" or
bnf_name like "%Seroxat%" or
bnf_name like "%sertraline%" or
bnf_name like "%Lustral%"
group by period;

+-------------------------+---------------------+
| Serotonin prescriptions | selective_serotonin |
+-------------------------+---------------------+
|                 2742049 | 201601              |
|                 2725157 | 201602              |
+-------------------------+---------------------+
2 rows in set (27.81 sec)

```


f) Visualise the top 10 practices by number of metformin prescriptions throughout the entire period.

```
select practice, sum(items) as "metformin prescriptions" from treatment where bnf_name like "%metformin%" group by practice order by sum(items) desc limit 10;
+----------+-------------------------+
| practice | metformin prescriptions |
+----------+-------------------------+
| M85063   |                    3192 |
| K83002   |                    2848 |
| C82024   |                    2810 |
| F84006   |                    2739 |
| C83019   |                    2652 |
| C83064   |                    2545 |
| D82044   |                    2264 |
| F84087   |                    2183 |
| J82155   |                    2108 |
| Y01008   |                    2083 |
+----------+-------------------------+


10 rows in set (12.93 sec)

select bnf_code, sum(items) as "metformin prescriptions", bnf_name from treatment where bnf_name like "%metformin%" group by bnf_name order by sum(items) desc;
+-----------------+-------------------------+------------------------------------------+
| bnf_code        | metformin prescriptions | bnf_name                                 |
+-----------------+-------------------------+------------------------------------------+
| 0601022B0AAABAB |                 2072307 | Metformin HCl_Tab 500mg                  |
| 0601022B0AAASAS |                  459598 | Metformin HCl_Tab 500mg M/R              |
| 0601022B0AAAVAV |                  254163 | Metformin HCl_Tab 1g M/R                 |
| 0601022B0AAADAD |                  246856 | Metformin HCl_Tab 850mg                  |
| 0601022B0AAATAT |                   31134 | Metformin HCl_Tab 750mg M/R              |
| 0601023ADAAAAAA |                   19558 | Metformin HCl/Sitagliptin_Tab 1g/50mg    |
| 0601023W0AAAAAA |                    9657 | Pioglitazone/Metformin HCl_Tab15mg/850mg |
| 0601022B0AAARAR |                    8771 | Metformin HCl_Oral Soln 500mg/5ml S/F    |
| 0601023Z0AAAAAA |                    8035 | Vildagliptin/Metformin HCl_Tab 50mg/1g   |
| 0601023AFAAABAB |                    4900 | Linagliptin/Metformin_Tab 2.5mg/1g       |
| 0601023AJAAAAAA |                    2846 | Alogliptin/Metformin_Tab 12.5mg/1g       |
| 0601023Z0AAABAB |                    1984 | Vildagliptin/Metformin HCl_Tab50mg/850mg |
| 0601023ALAAABAB |                    1533 | Dapagliflozin/Metformin_Tab 5mg/1g       |
| 0601023AHAAABAB |                    1372 | Saxagliptin/Metformin_Tab 2.5mg/1g       |
| 0601023AFAAAAAA |                     817 | Linagliptin/Metformin_Tab 2.5mg/850mg    |
| 0601023APAAABAB |                     628 | Canagliflozin/Metformin_Tab 50mg/1g      |
| 0601023AHAAAAAA |                     226 | Saxagliptin/Metformin_Tab 2.5mg/850mg    |
| 0601023ALAAAAAA |                     209 | Dapagliflozin/Metformin_Tab 5mg/850mg    |
| 0601023ARAAADAD |                     174 | Empagliflozin/Metformin_Tab 12.5mg/1g    |
| 0601023APAAAAAA |                      95 | Canagliflozin/Metformin_Tab 50mg/850mg   |
| 0601023ARAAABAB |                      90 | Empagliflozin/Metformin_Tab 5mg/1g       |
| 0601022B0AAAIAI |                      38 | Metformin HCl_Liq Spec 500mg/5ml         |
| 0601023ARAAACAC |                      29 | Empagliflozin/Metformin_Tab 12.5mg/850mg |
| 0601022B0AAAXAX |                      22 | Metformin HCl_Pdr Sach 1g S/F            |
| 0601023ARAAAAAA |                      16 | Empagliflozin/Metformin_Tab 5mg/850mg    |
| 0601022B0AAAWAW |                       8 | Metformin HCl_Pdr Sach 500mg S/F         |
| 0601022B0AAANAN |                       1 | Metformin HCl_Liq Spec 5mg/5ml           |
+-----------------+-------------------------+------------------------------------------+
27 rows in set (13.04 sec)


select left(bnf_code,9) , sum(items) as "metformin prescriptions" from treatment where bnf_name like "%metformin%" group by left(bnf_code,9) order by sum(items) desc;
+------------------+-------------------------+
| left(bnf_code,9) | metformin prescriptions |
+------------------+-------------------------+
| 0601022B0        |                 3072898 |
| 0601023AD        |                   19558 |
| 0601023Z0        |                   10019 |
| 0601023W0        |                    9657 |
| 0601023AF        |                    5717 |
| 0601023AJ        |                    2846 |
| 0601023AL        |                    1742 |
| 0601023AH        |                    1598 |
| 0601023AP        |                     723 |
| 0601023AR        |                     309 |
+------------------+-------------------------+
10 rows in set (13.00 sec)

select practice, sum(items) as "metformin prescriptions" from treatment where
left(bnf_code, 9) = "0601022B0" or
left(bnf_code, 9) = "0601023AD" or
left(bnf_code, 9) = "0601023Z0" or
left(bnf_code, 9) = "0601023W0" or
left(bnf_code, 9) = "0601023AF" or
left(bnf_code, 9) = "0601023AJ" or
left(bnf_code, 9) = "0601023AH" or
left(bnf_code, 9) = "0601023AL" or
left(bnf_code, 9) = "0601023AP" or
left(bnf_code, 9) = "0601023AR"
group by practice order by sum(items) desc limit 10;
+----------+-------------------------+
| practice | metformin prescriptions |
+----------+-------------------------+
| M85063   |                    3254 |
| K83002   |                    2943 |
| C82024   |                    2840 |
| F84006   |                    2745 |
| C83019   |                    2668 |
| C83064   |                    2560 |
| D82044   |                    2359 |
| F84087   |                    2183 |
| J82155   |                    2113 |
| Y01008   |                    2094 |
+----------+-------------------------+
10 rows in set (18.51 sec)
```


## Task 4: Observations of Database

### Task 3.a

There was discrepency in the practice ids is in the surgery_data table and the surgery table.
// TODO


select totalAll, practice from surgery_data where
practice = "F85017" or
practice = "F85019" or
practice = "F85028" or
practice = "F85030" or
practice = "F85615" or
practice = "F85628" or
practice = "Y04848";


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

* http://www.nhs.uk/conditions/beta-blockers/pages/introduction.aspx

* http://www.burrswood.org.uk/

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
