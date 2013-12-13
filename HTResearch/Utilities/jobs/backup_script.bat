#!/bin/bash
REM Create backup Mongo database dumpfile weekly using mongodump

REM Change this to your path, will make a relative path at some point
mongodump --host unlht.cloudapp.net --port 27017 --db ht --out "C:\Users\Brian\dump"

REM Restore using 
REM mongorestore --host unlht.cloudapp.net --port 27017 -collection <collection name> -db <db name> <path loading from (bson file)>