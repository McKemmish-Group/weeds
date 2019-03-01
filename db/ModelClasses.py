#!/usr/bin/python

import sys

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relation, exc, column_property, validates
from sqlalchemy import orm
from sqlalchemy.orm.session import Session

from DatabaseConnection import DatabaseConnection

dbc = DatabaseConnection()

# ========================
# Define database classes
# ========================
Base = declarative_base(bind=dbc.engine)

class Isotopologue(Base):
	__tablename__ = 'isotopologue'
	__table_args__ = {'autoload' : True}
	
class Transition(Base):
	__tablename__ = 'transition'
	__table_args__ = {'autoload' : True}

class EnergyLevel(Base):
	__tablename__ = 'energylevel'
	__table_args__ = {'autoload' : True}
    


# =========================
# Define relationships here
# =========================
#Transition.isotopologues = relation(Isotopologue, backref='transitions')

Transition.isotopologue = relation(Isotopologue, primaryjoin = Transition.isotopologue_id==Isotopologue.id, foreign_keys = [Transition.isotopologue_id], backref="transitions")
									
Transition.upper = relation(EnergyLevel, primaryjoin = Transition.upper_id==EnergyLevel.id, foreign_keys = [Transition.upper_id], backref="up_transitions")

Transition.lower = relation(EnergyLevel, primaryjoin = Transition.lower_id==EnergyLevel.id, foreign_keys = [Transition.lower_id], backref="low_transitions")

EnergyLevel.isotopologue = relation(Isotopologue, primaryjoin = EnergyLevel.isotopologue_id==Isotopologue.id,foreign_keys = [EnergyLevel.isotopologue_id], backref="energylevels")
									
#EnergyLevel.up_transitions = relation(Transition, primaryjoin = EnergyLevel.id==Transition.upper, foreign_keys = [EnergyLevel.id], backref="up_energylevels")

#EnergyLevel.low_transitions = relation(Transition, primaryjoin = EnergyLevel.id==Transition.lower, foreign_keys = [EnergyLevel.id], backref="low_energylevels")

#Isotopologue.energylevels = relation(EnergyLevel, primaryjoin = Isotopologue.id==EnergyLevel.isotopologue, foreign_keys = [Isotopologue.id], backref="energylevels")


# ---------------------------------------------------------
# Test that all relations/mappings are self-consistent.
# ---------------------------------------------------------

from sqlalchemy.orm import configure_mappers
try:
	configure_mappers()
except RuntimeError:
	print("""
An error occurred when verifying the relations between the database tables.
Most likely this is an error in the definition of the SQLAlchemy relations - 
see the error message below for details.
""")
	print("Error type: %s" % sys.exc_info()[0])
	print("Error value: %s" % sys.exc_info()[1])
	print("Error trace: %s" % sys.exc_info()[2])
	sys.exit(1)
