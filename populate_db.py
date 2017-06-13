from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from time import gmtime, strftime

from database_setup import Base, Chemical, Surgery, SurgeryData, Treatment


def readChemicals(file):

	duplicates = []

	f = open(file)
	lineCounter = 0

	for line in f:
		items = line.split(",")
		chem_sub, name = stripWhiteSpaces(items[0]), stripWhiteSpaces(items[1])
		chem = Chemical(chemical_sub_code = chem_sub, name=name)
		session.add(chem)
		session.commit()

	f.close()

class FileReader:



	def getSession(self):
		engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/PrescriptionsDB')
		# Bind the engine to the metadata of the Base class so that the
		# declaratives can be accessed through a DBSession instance
		Base.metadata.bind = engine

		DBSession = sessionmaker(bind=engine)
		# A DBSession() instance establishes all conversations with the database
		# and represents a "staging zone" for all the objects loaded into the
		# database session object. Any change made against the objects in the
		# session won't be persisted into the database until you call
		# session.commit(). If you're not happy about the changes, you can
		# revert all of them back to the last commit by calling
		# session.rollback()
		session = DBSession()
		return session

	def readChemicals(self, file):

		duplicates = []
		errors  =[]

		session  = self.getSession()

		f = open(file)
		lineCounter = 0

		first_line = f.readline() ## SKIP HEADERS

		for line in f:
			items = line.split(",")
			chem_sub, name = self.stripWhiteSpaces(items[0]), self.stripWhiteSpaces(items[1])
			# if chem_sub does not exist in db
			if session.query(Chemical.id).filter(Chemical.chemical_sub_code==chem_sub).count() == 0:
				try:
					chem = Chemical(chemical_sub_code = chem_sub, name=name)
					session.add(chem)
					session.commit()
				except:
					errors.append(chem_sub)
			else:
				duplicates.append(chem_sub)
			lineCounter += 1

		print("")
		print("UPLOAD REPORT:", file)
		print("Lines parsed: ",lineCounter)
		print("Errors: ", len(errors))
		print("Duplicates: ", len(duplicates))


		f.close()



	def readSurgeries(self, file):

		duplicates = []
		errors = []

		session  = self.getSession()

		f = open(file)
		lineCounter = 0

		for line in f:
			items = line.split(",")

			gp_id = self.stripWhiteSpaces(items[1])
			if session.query(Surgery.gp_id).filter(Surgery.gp_id==gp_id).count() == 0:
				try:
					gp = Surgery(
						gp_id = gp_id,
						name= self.stripWhiteSpaces(items[2]),
						addressOne= self.stripWhiteSpaces(items[3]),
						addressTwo= self.stripWhiteSpaces(items[4]),
						city= self.stripWhiteSpaces(items[5]),
						county = self.stripWhiteSpaces(items[6]),
						postcode = self.stripWhiteSpaces(items[7])
					)
					session.add(gp)
					session.commit()
				except:
					errors.append(gp_id)
			else:
				duplicates.append(gp_id)

			lineCounter += 1

		print("")
		print("UPLOAD REPORT:", file)
		print("Lines parsed: ",lineCounter)
		print("Errors: ", len(errors))
		print("Duplicates: ", len(duplicates))

		f.close()

	def readSurgeriesData(self, file):

		duplicates = []
		errors = []

		session  = self.getSession()

		f = open(file)
		lineCounter = 0

		first_line = f.readline() ## SKIP HEADERS

		for line in f:
			items = line.split(",")

			gp_id = self.stripWhiteSpaces(items[0])

			try:
				data = SurgeryData(
					practice = gp_id,
					postcode = self.stripWhiteSpaces(items[1]),
					ons_ccg_code = self.stripWhiteSpaces(items[2]),
					ccg_code = self.stripWhiteSpaces(items[3]),
					ons_region_code = self.stripWhiteSpaces(items[4]),
					nhse_region_code = self.stripWhiteSpaces(items[5]),
					ons_comm_rgn_code = self.stripWhiteSpaces(items[6]),
					nhse_comm_region_code = self.stripWhiteSpaces(items[7]),
					totalAll = self.stripWhiteSpaces(items[8]),
					totalMale = self.stripWhiteSpaces(items[9]),
					totalFemale = self.stripWhiteSpaces(items[10]),
				)
				session.add(data)
				session.commit()
			except:
				errors.append(gp_id)


			lineCounter += 1

		print("")
		print("UPLOAD REPORT:", file)
		print("Lines parsed: ",lineCounter)
		print("Errors: ", len(errors))
		print("Duplicates: ", len(duplicates))

		f.close()

	def readTreatment(self, file, run):

		duplicates = []
		errors = []

		session  = self.getSession()

		f = open(file)
		lineCounter = 0

		first_line = f.readline() ## SKIP HEADERS

		for line in f:
			items = line.split(",")

			try:
				treatment = Treatment(
					sha = self.stripWhiteSpaces(items[0]),
					pct = self.stripWhiteSpaces(items[1]),
					practice = self.stripWhiteSpaces(items[2]),
					bnf_code = self.stripWhiteSpaces(items[3]),
					bnf_name = self.stripWhiteSpaces(items[4]),
					items = self.stripWhiteSpaces(items[5]),
					nic = self.stripWhiteSpaces(items[6]),
					act_cost = self.stripWhiteSpaces(items[7]),
					quantity = self.stripWhiteSpaces(items[8]),
					period = self.stripWhiteSpaces(items[9])
				)
				session.add(treatment)
				session.commit()
			except:
				errors.append(self.stripWhiteSpaces(items[3]))	#record bnf code as a near UID

			lineCounter += 1

		print("")
		print("UPLOAD REPORT:", file)
		print("Lines parsed: ",lineCounter)
		print("Errors: ", len(errors))
		print("Duplicates: ", len(duplicates))

		f.close()

	def stripWhiteSpaces(self, string):
		return str.lstrip(str.rstrip(string))

x = FileReader()


print("BEGIN EXECUTION AT: " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
x.readChemicals("T201601CHEMSUBS.CSV")

x.readChemicals("T201602CHEMSUBS.CSV")

x.readSurgeries("T201601ADDRBNFT.CSV")

x.readSurgeries("T201602ADDRBNFT.CSV")

x.readSurgeriesData("gp-reg-patients-prac-quin-age.csv")

print("BEGIN LARGE FILE 1: " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
x.readTreatment("T201601PDPIBNFT.CSV", 1) ## Int input is  fudge to make PK
print("BEGIN LARGE FILE 1: " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
x.readTreatment("T201602PDPIBNFT.CSV", 2) ## Int input is  fudge to make PK

print("COMPLETED: " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
