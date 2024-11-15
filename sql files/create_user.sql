USE cs191;

--     host="localhost", #Change to IP address/Domain name when hosted 
--     user="student",
--     password="password",
--     database="cs191"

ALTER USER student@localhost IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES ON cs191.* TO student@localhost;

FLUSH PRIVILEGES;

SHOW GRANTS FOR student@localhost;