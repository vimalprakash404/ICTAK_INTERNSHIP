import mysql.connector
import random
import string
from datetime import datetime, timedelta

# Configuration
MYSQL_HOST = 'localhost'  # Change this to your MySQL host
MYSQL_USER = 'root'  # Change this to your MySQL username
MYSQL_PASSWORD = ''  # Change this to your MySQL password
MYSQL_DB = 'BloodBank'  # Change this to your desired database name


# List of sample data
blood_groups = ['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']
cities = ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Kollam', 'Thrissur', 'Alappuzha', 'Kottayam', 'Palakkad', 'Malappuram', 'Kannur', 'Kasaragod', 'Pathanamthitta', 'Idukki', 'Wayanad', 'Thalassery', 'Vadakara', 'Kasaragod', 'Payyannur', 'Kanhangad', 'Aluva', 'Muvattupuzha', 'Thodupuzha', 'Kottarakkara', 'Adoor', 'Changanassery', 'Mannar', 'Nilambur', 'Kodungallur', 'Koyilandy', 'Perinthalmanna', 'Cherthala', 'Kottakkal', 'Nedumangad', 'Kayamkulam', 'Punalur', 'Neyyattinkara', 'Taliparamba', 'Chittur', 'Vatakara', 'Pappinisseri', 'Paravoor']
districts = [
        'Alappuzha',
        'Ernakulam',
        'Idukki',
        'Kannur',
        'Kasaragod',
        'Kollam',
        'Kottayam',
        'Kozhikode',
        'Malappuram',
        'Palakkad',
        'Pathanamthitta',
        'Thiruvananthapuram',
        'Thrissur',
        'Wayanad'
    ]
first_names = ['John', 'Jane', 'Michael', 'Emily', 'William', 'Emma', 'James', 'Olivia', 'Alexander', 'Sophia']
last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']
streets = ['First Street', 'Second Street', 'Third Street', 'Fourth Street', 'Fifth Street', 'Park Avenue', 'Main Street', 'Elm Street', 'Maple Avenue', 'Oak Street']

def generate_random_phone_number():
    return ''.join(random.choice(string.digits) for _ in range(10))

# Helper function to generate random date within the last year for last_donation_date
def generate_random_last_donation_date():
    current_date = datetime.now()
    last_year = current_date - timedelta(days=365)
    random_days = random.randint(0, (current_date - last_year).days)
    return last_year + timedelta(days=random_days)

# Generate 1000 rows of sample data for both tables
def generate_sample_data():
    donator_data = []
    login_data = []
    for i in range(1000):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        blood_group = random.choice(blood_groups)
        phone_number = generate_random_phone_number()
        city = random.choice(cities)
        house_name = f'House{i + 1}'
        street = random.choice(streets)
        last_donation_date = generate_random_last_donation_date().strftime('%Y-%m-%d')
        district = random.choice(districts)
        state = 'Kerala'
        country = 'India'
        donator_data.append((first_name, last_name, blood_group, last_donation_date, phone_number, house_name, street, city, district, state, country))

        # Generating login data
        username = f'{first_name.lower()}'
        password = f'{first_name.lower()}'
        login_data.append((username, password))

    return donator_data, login_data

# Insert the generated data into the "donator" table
def insert_sample_data():
    with mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    ) as db:
        cursor = db.cursor()
        donator_data, login_data = generate_sample_data()
        donator_id=[]
        # Generate and insert data for the "donator" table
        for donator_data_i in donator_data:
            
            donator_query = "INSERT INTO donator (first_name, last_name, blood_group, last_donation_date, phone_number, house_name, street, city, district, state, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(donator_query, donator_data_i)

        # Generate and insert data for the "donator_login" table
            donator_id.append(cursor.lastrowid) 
        
            # Insert into the donator_login table
        login_data1 = []
        for i,data in enumerate(login_data):
            login_data1.append((str(donator_id[i]),data[0]+str(donator_id[i]),data[1]+str(donator_id[i])))
        print(login_data1)
        login_query = "INSERT INTO donator_login (donator_id, username, password) VALUES (%s, %s, %s)"
        cursor.executemany(login_query, login_data1)
        

        db.commit()

if __name__ == "__main__":
    insert_sample_data()
    print("Sample data insertion complete.")
