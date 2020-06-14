# Client-Server Architecture for ERebuild

## Database Export

The process of exporting database with the help of phpmyadmin:

  1. Login to mileresearch.coe.fsu.edu/phpmyadmin.
  2. Select the database, go to Export and Select the table you want to migrate.
  3. Export as csv and save the file to `db_csvs` directory.

We might have to migrate away from the old database currently being hosted on mileresearch.coe.fsu.edu
because there will be new requirements in the future. We might want to alter the schema names
or even normalize the tables. 

  1. Modify the Python script `scripts/database_migration.py`: columns to delete, to rename or to add with default values.
  2. Run the script in 4. with appropriate arguments and generate the modified csv file.
  3. Insert the table content into the new database:

    - In the local sqlite3 database, create a new table with the column names from 4. For example,
    ```sql
    CREATE TABLE UserInfo ( 
      user_email VARCHAR NOT NULL PRIMARY KEY,
      user_password VARCHAR NOT NULL,
      user_firstname TEXT,
      user_lastname TEXT,
      user_school TEXT,
      user_class TEXT,
      user_type INT NOT NULL);
    ```

    From the sqlite3 terminal:
    ```bash
    sqlite> .mode csv
    sqlite> .import db_csvs/erebuild_UserInfo.csv UserInfo
    ```

    The column order in the csv should be the same as in the created table. 
    Also, delete the header in the transformed csv file before importing it to the database.

## Database Migration

Create a new mysql database in a Linux server from the mysql database dump obtained from Windows server.
This need arose when I wanted to run tests on a snapshot of the production database.

1. Create a MySQL dump with `mysqldump.exe`
    ```console
    mysqldump.exe --single-transaction -u user -p password -h localhost db_name > db_name_dump.sql
    ```
    
2. Transfer `db_name_dump.sql` to your Linux machine

3. Assume you are now in a Linux machine. `db_name_dump.sql` may not be encoded in utf-8::
    ```console
    $ # Find out what encoding the file has from the terminal.
    $ file -i db_name_dump.sql
    db_name_dump.sql: text/plain; charset=utf-16le
    
    $ # Convert the encoding
    $ iconv -f utf-16le  -t utf-8 db_name_dump.sql -o db_name_dump_utf8.sql
    ```
    
4. Create a new mysql database that will eventually hold the contents of the dump

    ```console
    $ mysql -u user -p 
    > create database db_name;
    > exit
    ```

5. Load data from the dump into the new mysql database::

    ```console
    $ mysql -u root -p db_name < db_name_dump_utf8.sql
    ```
