from flask import session,Flask, render_template, request, redirect, url_for,flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "vimal"
# Configuration
app.config['MYSQL_HOST'] = 'localhost'  # Change this to your MySQL host
app.config['MYSQL_USER'] = 'your_username'  # Change this to your MySQL username
app.config['MYSQL_PASSWORD'] = 'your_password'  # Change this to your MySQL password
app.config['MYSQL_DB'] = 'blood_donation_db'  # Change this to your desired database name

# Helper function to connect to the database
def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='BloodBank'
    )

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'


def get_all_registered_users():
    with get_db() as db:
        cursor = db.cursor()
        query = "SELECT * FROM donator"
        cursor.execute(query)
        return cursor.fetchall()
# Helper function to check if the user is logged in as an admin
def is_admin_logged_in():
    return 'admin_username' in session

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the entered credentials match the admin credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # If the credentials match, set the admin_username in the session
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            # If the credentials don't match, show an error message
            error = 'Invalid credentials. Please try again.'
            return render_template('admin_login.html', error=error)

    return render_template('admin_login.html')

def get_unique_cities():
    with get_db() as db:
        cursor = db.cursor()
        query = "SELECT name FROM city"
        cursor.execute(query)
        cities = cursor.fetchall()
        return [city[0] for city in cities]
    
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    cities = get_unique_cities()
    selected_city = request.form.get('city', '')  # Get the selected city from the form
    selected_blood_group = request.form.get('blood_group', '') 
    # Fetch all registered users based on the selected city filter
    with get_db() as db:
        cursor = db.cursor()
        if selected_city and selected_blood_group:
            query = "SELECT * FROM donator WHERE city = %s AND blood_group = %s"
            cursor.execute(query, (selected_city,selected_blood_group))
        elif selected_city:
            query = "SELECT * FROM donator WHERE city = %s"
            cursor.execute(query, (selected_city,))
        elif selected_blood_group:
            query = "SELECT * FROM donator WHERE blood_group = %s"
            cursor.execute(query, (selected_blood_group,))
        else:
            query = "SELECT * FROM donator"
            cursor.execute(query)

        users = cursor.fetchall()

    blood_groups = get_unique_blood_groups()
     # Get the selected blood group from the form

    # Apply blood group filter if selected
    # if selected_blood_group:
    #     users = [user for user in users if user[3] == selected_blood_group]

    # if selected_city and selected_blood_group:
    #     users = [user for user in users if user[3] == selected_blood_group and user[10] == selected_city]

    return render_template('admin_dashboard.html', admin_username=session['admin_username'], users=users, cities=cities, selected_city=selected_city, blood_groups=blood_groups, selected_blood_group=selected_blood_group)

@app.route('/donor/search', methods=['GET', 'POST'])
def search_donors():
    if not is_logged_in():
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    donator_id = session['user_id']
    cities = get_unique_cities()
    selected_city = request.form.get('city', '')  # Get the selected city from the form

    # Fetch all registered users based on the selected city filter
    with get_db() as db:
        cursor = db.cursor()
        if selected_city:
            query = "SELECT * FROM donator WHERE city = %s"
            cursor.execute(query, (selected_city,))
        else:
            query = "SELECT * FROM donator"
            cursor.execute(query)

        users = cursor.fetchall()

    blood_groups = get_unique_blood_groups()
    selected_blood_group = request.form.get('blood_group', '')  # Get the selected blood group from the form

    # Apply blood group filter if selected
    if selected_blood_group:
        users = [user for user in users if user[3] == selected_blood_group]

    return render_template('donor_search.html', donor_id=session['user_id'], users=users, cities=cities, selected_city=selected_city, blood_groups=blood_groups, selected_blood_group=selected_blood_group)


def delete_donator_by_id(donator_id):
    print(donator_id)
    with get_db() as db:
        cursor = db.cursor()
        query = "DELETE FROM donator_login WHERE donator_id = %s"
        cursor.execute(query, (donator_id,))
        query = "DELETE FROM donator WHERE id = %s"
        cursor.execute(query, (donator_id,))
        db.commit()

@app.route('/admin/delete_donator/<int:donator_id>', methods=['POST'])
def delete_donator(donator_id):
    if not is_admin_logged_in():
        # If admin is not logged in, redirect to the admin login page
        return redirect(url_for('admin_login'))

    delete_donator_by_id(donator_id)
    flash('Donator deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

def get_unique_blood_groups():
    with get_db() as db:
        cursor = db.cursor()
        query = "SELECT DISTINCT blood_group FROM donator"
        cursor.execute(query)
        blood_groups = cursor.fetchall()
        return [group[0] for group in blood_groups]

@app.route('/register', methods=['GET', 'POST'])
def register_donator():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        blood_group = request.form['blood_group']
        last_donation_date = request.form['last_donation_date']
        phone_number = request.form['phone_number']
        house_name = request.form['house_name']
        street = request.form['street']
        city = request.form['city']
        district = request.form['district']
        state = request.form['state']
        country = request.form['country']
        username = request.form['username']
        password = request.form['password']

        # Store the donor information in the database
        
        with get_db() as db:
            cursor = db.cursor()
            # Insert into the donator table
            cursor.execute('INSERT INTO donator (first_name, last_name, blood_group, last_donation_date, phone_number, house_name, street, city, district, state, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (first_name, last_name, blood_group, last_donation_date, phone_number, house_name, street, city, district, state, country))
            # Get the inserted donator's ID
            donator_id = cursor.lastrowid
            # Insert into the donator_login table
            cursor.execute('INSERT INTO donator_login (donator_id, username, password) VALUES (%s, %s, %s)',
                           (donator_id, username, password))
            db.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('index'))
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT name FROM city')
        cities = [city[0] for city in cursor.fetchall()]
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
    print(cities)
    return render_template('register.html', cities=cities,districts=districts)

def is_logged_in():
    return 'user_id' in session

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the entered credentials match the admin credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # If the credentials match, set the admin_username in the session
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            # If the credentials don't match, show an error message
            if request.method == 'POST':
                    username = request.form['username']
                    password = request.form['password']

                    # Verify the credentials against the donator_login table
                    with get_db() as db:
                        cursor = db.cursor(dictionary=True)
                        cursor.execute('SELECT * FROM donator_login WHERE username = %s', (username,))
                        donator = cursor.fetchone()

                        if donator and donator['password'] == password:
                            # Successful login, set the 'user_id' in the session
                            session['user_id'] = donator['donator_id']
                            flash('You are now logged in!', 'success')
                            return redirect(url_for('donator_home'))
                        else:
                            flash('Invalid credentials. Please try again.', 'danger')

            return render_template('login.html')

    return render_template('login.html')
    

@app.route('/donator_home')
def donator_home():
    if not is_logged_in():
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    donator_id = session['user_id']

    # Fetch the donator's details from the database based on their ID
    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM donator WHERE id = %s', (donator_id,))
        donator = cursor.fetchone()

    if not donator:
        flash('Donator not found.', 'danger')
        return redirect(url_for('login'))

    return render_template('donator_home.html', donator=donator)
@app.route('/logout')
def logout():
    # Clear the 'user_id' from the session to log the user out
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/admin/add_city', methods=['GET', 'POST'])
def add_city():
    if not is_admin_logged_in():
        # If admin is not logged in, redirect to the admin login page
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        new_city = request.form.get('city', '').strip()

        # Validate if city is not empty
        if not new_city:
            flash('City name cannot be empty.', 'error')
        else:
            # Add the new city to the city table in the database
            with get_db() as db:
                cursor = db.cursor()
                query = "INSERT INTO city (name) VALUES (%s)"
                cursor.execute(query, (new_city,))
                db.commit()

            flash(f'City "{new_city}" added successfully.', 'success')

    return render_template('add_city.html', admin_username=session['admin_username'])
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/donor/edit', methods=['GET', 'POST'])
def edit_user_info():
    if not is_logged_in():
        # If donor is not logged in, redirect to the donor login page
        return redirect(url_for('login'))

    donor_id = session['user_id']

    with get_db() as db:
        cursor = db.cursor()
        if request.method == 'POST':
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            blood_group = request.form.get('blood_group', '')
            last_donation_date = request.form.get('last_donation_date', '')
            phone_number = request.form.get('phone_number', '').strip()
            address = request.form.get('address', '').strip()
            street = request.form.get('street',).strip()
            city = request.form.get('city',).strip()

            # Update the user information in the donator table
            query = "UPDATE donator SET first_name = %s, last_name = %s, blood_group = %s, last_donation_date = %s, phone_number = %s, house_name = %s,street= %s,city = %s   WHERE id = %s"
            cursor.execute(query, (first_name, last_name, blood_group, last_donation_date, phone_number, address,street,city, donor_id))
            db.commit()

            flash('Your information has been updated successfully.', 'success')

        # Fetch the current user information
        query = "SELECT * FROM donator WHERE id = %s"
        cursor.execute(query, (donor_id,))
        user_info = cursor.fetchone()
    cities = get_unique_cities()
    return render_template('edit_user_info.html', user_info=user_info,cities = cities)

if __name__ == '__main__':
    app.run(debug=True)
