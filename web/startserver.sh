#!/bin/bash

echo creating schema
echo mysql -h ${DBHOST} -uroot -predacted ssa < schema.sql
mysql -h ${DBHOST} -uroot -p${MYSQL_ROOT_PASSWORD}  ssa < schema.sql
echo maybe created schema
python3 ./server.py 80
