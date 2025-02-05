from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import jdatetime
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Load MySQL configuration from environment variables for security
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'radius')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'radius')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'radius')

mysql = MySQL(app)

# Secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', 'testing123')


@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')


@app.route('/set_bandwidth/<string:username>', methods=['GET', 'POST'])
def set_bandwidth(username):
    """Set bandwidth limits for a user."""
    if request.method == 'POST':
        max_upload_speed = request.form.get('max_upload_speed', '0')
        max_download_speed = request.form.get('max_download_speed', '0')

        try:
            with mysql.connection.cursor() as cur:
                # Remove existing bandwidth limits
                cur.execute("""
                    DELETE FROM radreply 
                    WHERE username = %s 
                    AND attribute IN ('WISPr-Bandwidth-Max-Up', 'WISPr-Bandwidth-Max-Down')
                """, (username,))

                # Insert new limits
                cur.executemany("""
                    INSERT INTO radreply (username, attribute, op, value) 
                    VALUES (%s, %s, ':=', %s)
                """, [
                    (username, 'WISPr-Bandwidth-Max-Up', max_upload_speed),
                    (username, 'WISPr-Bandwidth-Max-Down', max_download_speed)
                ])

                mysql.connection.commit()
            flash('Bandwidth limits updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating bandwidth limits: {e}', 'danger')

        return redirect(url_for('users'))

    return render_template('set_bandwidth.html', username=username)


@app.route('/delete_bandwidth/<string:username>', methods=['POST'])
def delete_bandwidth(username):
    """Delete bandwidth limits for a user."""
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
                DELETE FROM radreply 
                WHERE username = %s 
                AND attribute IN ('WISPr-Bandwidth-Max-Up', 'WISPr-Bandwidth-Max-Down')
            """, (username,))
            mysql.connection.commit()
        flash('Bandwidth limits deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting bandwidth limits: {e}', 'danger')

    return redirect(url_for('users'))


@app.route('/users')
def users():
    """Retrieve and display user details."""
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
                SELECT r.username,
                       MAX(CASE WHEN r.attribute = 'Cleartext-Password' THEN r.value END) AS password,
                       MAX(CASE WHEN rr.attribute = 'WISPr-Bandwidth-Max-Up' THEN rr.value END) AS max_upload_speed,
                       MAX(CASE WHEN rr.attribute = 'WISPr-Bandwidth-Max-Down' THEN rr.value END) AS max_download_speed
                FROM radcheck r
                LEFT JOIN radreply rr ON r.username = rr.username
                GROUP BY r.username
            """)
            users = cur.fetchall()
        return render_template('users.html', users=users)
    except Exception as e:
        flash(f'Error fetching users: {e}', 'danger')
        return render_template('users.html', users=[])


@app.route('/add_user', methods=['POST'])
def add_user():
    """Add a new user to the database."""
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username and password are required!', 'warning')
        return redirect(url_for('users'))

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("""
                INSERT INTO radcheck (username, attribute, op, value) 
                VALUES (%s, 'Cleartext-Password', ':=', %s)
            """, (username, password))
            mysql.connection.commit()
        flash('User added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding user: {e}', 'danger')

    return redirect(url_for('users'))


@app.route('/delete_user/<string:username>', methods=['POST'])
def delete_user(username):
    """Delete a user and associated data from the database."""
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("DELETE FROM radcheck WHERE username = %s", (username,))
            cur.execute("DELETE FROM radreply WHERE username = %s", (username,))
            mysql.connection.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {e}', 'danger')

    return redirect(url_for('users'))


@app.route('/update_user/<string:username>', methods=['GET', 'POST'])
def update_user(username):
    """Update a user's password."""
    if request.method == 'POST':
        new_password = request.form.get('password')

        if not new_password:
            flash('Password cannot be empty!', 'warning')
            return redirect(url_for('users'))

        try:
            with mysql.connection.cursor() as cur:
                cur.execute("UPDATE radcheck SET value = %s WHERE username = %s", (new_password, username))
                mysql.connection.commit()
            flash('User password updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating user: {e}', 'danger')

        return redirect(url_for('users'))

    return render_template('update_user.html', username=username)


@app.route('/usage', methods=['GET'])
def usage():
    """Retrieve and display user bandwidth usage based on Jalali or Gregorian dates."""
    date_type = request.args.get('date_type', 'jalali')  # Default to Jalali if not provided
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        today = jdatetime.date.today()
        if date_type == 'jalali':
            # Convert Jalali dates to Gregorian
            start_date_gregorian = (
                jdatetime.datetime.strptime(start_date, '%Y/%m/%d').togregorian().strftime('%Y-%m-%d')
                if start_date else today.replace(day=1).togregorian().strftime('%Y-%m-%d')
            )
            end_date_gregorian = (
                jdatetime.datetime.strptime(end_date, '%Y/%m/%d').togregorian().strftime('%Y-%m-%d')
                if end_date else today.togregorian().strftime('%Y-%m-%d')
            )
        else:
            # Use provided Gregorian dates directly
            start_date_gregorian = start_date if start_date else today.replace(day=1).strftime('%Y-%m-%d')
            end_date_gregorian = end_date if end_date else today.strftime('%Y-%m-%d')

        with mysql.connection.cursor() as cur:
            cur.execute("""
                SELECT a.username, 
                       COALESCE(SUM(a.acctinputoctets) / 1073741824, 0) AS total_download_gb, 
                       COALESCE(SUM(a.acctoutputoctets) / 1073741824, 0) AS total_upload_gb, 
                       COALESCE(SUM(a.acctinputoctets + a.acctoutputoctets) / 1073741824, 0) AS total_usage_gb
                FROM radacct a
                WHERE (a.acctstarttime BETWEEN %s AND %s)
                   OR (a.acctstoptime BETWEEN %s AND %s)
                GROUP BY a.username
            """, (start_date_gregorian, end_date_gregorian, start_date_gregorian, end_date_gregorian))

            usage_data = cur.fetchall()

        return render_template('usage.html', usage_data=usage_data, date_type=date_type)
    except Exception as e:
        flash(f'Error fetching usage data: {e}', 'danger')
        return render_template('usage.html', usage_data=None, date_type=date_type)


if __name__ == '__main__':
    app.run(debug=False, port=5003)
