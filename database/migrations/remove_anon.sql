DELETE FROM mysql.user WHERE User='';
FLUSH PRIVILEGES;
SELECT User, Host FROM mysql.user;
