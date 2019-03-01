#!/usr/bin/python
#

__author__ = 'Demitri Muna <demitri@scicoder.org>'
''' -----------------------------------------------------------------------
Usage:

This class defines a connection to a database and is
implemented as a singleton.

It can be used in one of two ways (in order by recommendation):

1)

Create a class containing the specific connection details that
will create the first instance of DatabaseConnection (defined below),
which makes the initial connection to the database.

Then in your script, you then call that script, NOT this one:

from MyConnection import db # access to engine, metadata, Session
from MyModelClasses import *
...
session = db.Session()
...

Make sure you import ModelClasses AFTER the database connection class.

2)

To use this class directly, you must define a database
connection string.

Then in your script:

from DatabaseConnection import DatabaseConnection

db = DatabaseConnection(database_connection_string)
...
session = db.Session()
...

where "database_connection_string" is the connection string specific
to the type of database you are connecting to as defined in the
SQLAlchemy (http://www.sqlalchemy.com/) documentation.

Note: This class provides access to the following (as needed, but
 most likely you won't need these):
 
db.engine
db.metadata
db.Base (the superclass of classes mapped to database tables)

 --------------------------------------------------------------------------
'''

import os
import sqlalchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.event import listen
from sqlalchemy.pool import Pool

import NumpyAdaptorsSQLite
#import NumpyAdaptorsPostgreSQL

def clearSearchPathCallback(dbapi_con, connection_record):
    '''
    When creating relationships across schema, SQLAlchemy
    has problems when you explicitly declare the schema in
    ModelClasses and it is found in search_path.
    
    The solution is to set the search_path to "$user" for
    the life of any connection to the database. Since there
    is no (or shouldn't be!) schema with the same name
    as the user, this effectively makes it blank.
    
    This callback function is called for every database connection.
    
    For the full details of this issue, see:
    http://groups.google.com/group/sqlalchemy/browse_thread/thread/88b5cc5c12246220
    
    dbapi_con - type: psycopg2._psycopg.connection
    connection_record - type: sqlalchemy.pool._ConnectionRecord
    '''
    cursor = dbapi_con.cursor()
    cursor.execute('SET search_path TO "$user",functions')
    dbapi_con.commit()

#listen(Pool, 'connect', clearSearchPathCallback)

class DatabaseConnection(object):
	'''This class defines an object that makes a connection to a database.
	   The "DatabaseConnection" object takes as its parameter the SQLAlchemy
	   database connection string.

	   This class is best called from another class that contains the
	   actual connection information (so that it can be reused for different
	   connections).
	   
	   This class implements the singleton design pattern. The first time the
	   object is created, it *requires* a valid database connection string.
	   Every time it is called via:
	   
	   db = DatabaseConnection()
	   
	   the same object is returned and contains the connection information.
	'''
	_singletons = dict()
	
	def __new__(cls, database_connection_string=None):
		"""This overrides the object's usual creation mechanism."""

		if not cls in cls._singletons:
			assert database_connection_string is not None, "A database connection string must be specified!"
			cls._singletons[cls] = object.__new__(cls)
			
			# ----------------------
			# Postgres-only commands
			# ----------------------
			if 'postgresql' in database_connection_string:
			    listen(Pool, 'connect', clearSearchPathCallback)
			
			# ------------------------------------------------
			# This is the custom initialization
			# ------------------------------------------------
			me = cls._singletons[cls] # just for convenience
			
			me.database_connection_string = database_connection_string
			
			# change 'echo' to print each SQL query (for debugging/optimizing/the curious)
			me.engine = create_engine(me.database_connection_string, echo=False)	

			me.metadata = MetaData()
			me.metadata.bind = me.engine
			# ------------------------------------------------
		
		return cls._singletons[cls]


'''
Reference: http://www.sqlalchemy.org/docs/05/reference/orm/sessions.html#sqlalchemy.orm.sessionmaker

autocommit = True : this prevents postgres from deadlocking on long-lived session processes (e.g. a background daemon), that produces 'idle in transaction' processes in PostgreSQL.
autoflush = False: prevents flushing (i.e. commiting) objects when only performing a SELECT statement, i.e. when not modifying the db

Sample code to account for different cases (if things change for whatever reason):

if session.autocommit:
	session.begin()
<do stuff>
session.commit()

Try to minimise the work done in between session.begin() and session.commit().
'''
