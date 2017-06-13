import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()



class Chemical(Base):

	__tablename__ = 'chemical'

	id = Column(Integer, primary_key = True)
	chemical_sub_code = Column(String(20), nullable=False, unique = True)
	name = Column(String(100), nullable = False, unique = False)

class Surgery(Base):

	__tablename__ = 'surgery'

	id = Column(Integer, primary_key = True)
	gp_id = Column(String(20), unique = True)
	name = Column(String(100), nullable = False, unique = False)
	addressOne = Column(String(100), nullable = False, unique = False)
	addressTwo = Column(String(100), nullable = False, unique = False)
	city = Column(String(100), nullable = False, unique = False)
	county = Column(String(100), nullable = False, unique = False)
	postcode = Column(String(20), nullable = False, unique = False)

class SurgeryData(Base):

	__tablename__ = 'surgery_data'

	id = Column(Integer, primary_key = True)
	# Should be FK
	practice = Column(String(20), nullable = False)
	postcode = Column(String(20), nullable = False)
	ons_ccg_code = Column(String(20), nullable = False)
	ccg_code = Column(String(20), nullable = False)
	ons_region_code = Column(String(100), nullable = False)
	nhse_region_code = Column(String(100), nullable = False)
	ons_comm_rgn_code = Column(String(100), nullable = False)
	nhse_comm_region_code = Column(String(100), nullable = False)
	totalAll = Column(Integer)
	totalMale = Column(Integer)
	totalFemale = Column(Integer)

class Treatment(Base):

	__tablename__ = 'treatment'

	id = Column(Integer, primary_key = True)
	sha = Column(String(10), nullable = False, unique = False)
	pct = Column(String(20), nullable = False, unique = False)
	# Should eb FK
	practice = Column(String(20), nullable = False, unique = False)
	bnf_code = Column(String(20), nullable = False, unique = False)
	bnf_name = Column(String(100), nullable = False, unique = False)
	items = Column(Integer, nullable = False, unique = False)
	nic = Column(Float, nullable = False, unique = False)
	act_cost = Column(Float, nullable = False, unique = False)
	quantity = Column(Integer, nullable = False, unique = False)
	period = Column(String(20), nullable = False, unique = False)

engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/PrescriptionsDB')
#'mysql+mysqldb://root:root@127.0.0.1:3306/nhscourework')


Base.metadata.create_all(engine)
