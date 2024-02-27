GET_CITIES = 'select * from city'
GET_COORDS = 'select latitude, longtitude from city where name=%s'
INSERT_CITY = 'insert into city (name, latitude, longtitude) values (%s, %s, %s)'
DELETE_CITY = 'delete from city where name=%s'
