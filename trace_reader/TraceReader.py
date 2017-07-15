import xlrd
import MySQLdb
# Open the workbook and define the worksheet
sheet_name = raw_input('Please specify table name: ')
book = xlrd.open_workbook("SampleData.xlsx")
sheet = book.sheet_by_name(sheet_name)

# Establish a MySQL connection
database = MySQLdb.connect (host="localhost", user = "root", passwd = "password", db = "mediconnect")

# Get the cursor, which is used to traverse the database, line by line
cursor = database.cursor()
# Create the INSERT INTO sql query
def create_query(table):
	if table == 'Rank' :
		query = """INSERT INTO rank (hospital,disease,rank ) VALUES (%s, %s, %s)"""
	if table == 'Hospital':
		query = """INSERT INTO hospital(name,overall_rank,email,area,website,introduction,feedback_time,price_range,slots_open,specialty) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
	if table == 'Disease':
		query = """INSERT INTO disease(name,keyword) VALUES (%s,%s)"""
	return query


# Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
def create_values(table):
	if table == 'Rank':
		query = create_query('Rank')
		for r in range(1, sheet.nrows):
		      hospital_name     = sheet.cell(r,0).value
		      disease_name      = sheet.cell(r,1).value
		      rank 		   = sheet.cell(r,2).value
		      cursor.execute("SELECT hospital.id FROM hospital WHERE name = '%s'" %(hospital_name))
		      hospital_id = cursor.fetchone()
		      cursor.execute("SELECT disease.id FROM disease WHERE name = '%s'" %(disease_name))
		      disease_id = cursor.fetchone()	
		      # Assign values from each row
		      values = (hospital_id,disease_id,rank)
		      cursor.execute(query,values)
	if table == 'Hospital':
		query = create_query('Hospital')
		print query
		for r in range(1,sheet.nrows):
			name 	 = sheet.cell(r,0).value
			overall_rank = sheet.cell(r,1).value
			feedback_time = sheet.cell(r,2).value
			price_range = sheet.cell(r,3).value
			specialty = sheet.cell(r,4).value
			slots_open = sheet.cell(r,5).value
			introduction = sheet.cell(r,6).value
			email = sheet.cell(r,7).value
			area = sheet.cell(r,8).value
			website = sheet.cell(r,9).value

			values = (name,overall_rank,email,area,website,introduction,feedback_time,price_range,slots_open,specialty)
			cursor.execute(query,values)
	if table == 'Disease':
		query = create_query('Disease')
		for r in range(1,sheet.nrows):
			name = sheet.cell(r,0).value
			keyword = sheet.cell(r,1).value
			values = (name,keyword)
			cursor.execute(query,values)

# Close the cursor
create_values(sheet_name)
cursor.close()

# Commit the transaction
database.commit()

# Close the database connection
database.close()

# Print results
print ""
print "All Done"
print ""
