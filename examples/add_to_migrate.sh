#!/bin/bash
#
# example of exporting
#

host='127.0.0.1'
port=63306
user='syscp'
passwd='somegoodpass!'
db='syscp'

# libido: export(mmysql)
mmysql() {
    extra=""
    if [[ "$1" == '--table' ]]
    then
        extra=--table
        shift
    fi
    if [[ "$1" == '--showq' ]]
    then
        # echo to stderr
        (>&2 echo "$2")
        shift
    fi
    mysql -h $host -P$port -u$user -p$passwd $extra $db <<< "$@"
}


if [[ -z "$1" ]]
then
    echo "need domain as parameter"
    exit 1
fi

sql="select 1 from migration_domain where domain = '$1'"
r=$(mmysql --showq "$sql")

if [[ -z "$r" ]]
then
    echo "site not found '$1'"
    sql="select domain from migration_domain where domain like '$1'"
    echo "$sql"
    mmysql --table "$sql"
    exit 1
fi

sql="update migration_domain set selected = True where domain = '$1'"
mmysql "$sql"

# fetch query for buldding yaml
sql="
select loginname, domain, type_site, db.databasename, c.documentroot,
    dd.customerid
from migration_domain as dd
join panel_customers as c using(customerid)
join panel_databases as db using(customerid)
where selected;
"

mmysql --table "$sql"
