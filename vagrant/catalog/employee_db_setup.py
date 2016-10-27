import os
import sys
from sqlalchemy import Column, \
                       ForeignKey, \
                       Integer, \
                       String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Create base class
Base = declarative_base()

# Create Restaurant class
class Employee(Base):
    '''
    Database for employees

    Employees in the employee table have an ID and a name.
    '''
    __tablename__ = 'employee'

    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)


# Create MenuItem class:
class Address(Base):
    '''
    Database for employee addresses

    Employees addresses have a street and a ZIP, an id as pk as well as an
    employee ID as a foreign key.
    '''
    __tablename__ = 'address'

    street = Column(String(80), nullable = False)
    zip = Column(String(8), nullable = False)
    id = Column(Integer, primary_key = True)
    employee_id = Column(Integer, ForeignKey('employee.id'))
    employee = relationship(Employee)

### Keep this at the end of the file ###
engine = create_engine('sqlite:///employeeData.db')
Base.metadata.create_all(engine)
