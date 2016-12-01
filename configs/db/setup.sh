#!/bin/sh

echo "Updating mysql configs in /etc/mysql/my.cnf."

#
# Update /etc/mysql/my.cnf
#
dialog --title 'Database configuration' --yesno '\nATN-SIM requires MySQL to accept incoming connections from all IPs. Can we configure that automatically for you?\n\n' 0 0 --output-fd 1

RESPONSE=$?

case $RESPONSE in
   0) sed -i "s/.*bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/my.cnf;;
   255) echo "\nAborting."; exit;;
esac


#
# Creating tables and grant permissions
#

while :
do
    DBUSER=$(dialog --title 'Database configuration' --inputbox '\nAdministrative user:' 0 0 --output-fd 1)
    DBPASS=$(dialog --title 'Database configuration' --passwordbox '\nPassword:' 0 0 --output-fd 1)

    if [ ${#DBPASS} -eq 0 ]; then
        # Connection WITHOUT password
        if mysql -u $DBUSER -e 'source db.sql'; then
            break
        fi
    else
        # Connection WITH password
        if mysql -u $DBUSER -p$DBPASS -e 'source db.sql'; then
            break
        fi
    fi

    dialog --title 'Database configuration' --msgbox '\nInvalid credentials.' 5 40
done

echo ""
echo "Restarting MySQL server"
sudo /etc/init.d/mysql stop
sudo /etc/init.d/mysql start

if [ "$RESPONSE" -eq 1 ]; then
    echo "+-------------------------------------------------------+"
    echo "+ Do not forget to update /etc/mysql/my.cnf as follows: +"
    echo "+                                                       +"
    echo "+ bind-address = 0.0.0.0                                +"
    echo "+-------------------------------------------------------+"
fi

echo "> Done!"