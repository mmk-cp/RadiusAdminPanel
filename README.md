# FreeRADIUS Manager for pfSense  
## Flask Web Application RADIUS Admin Panel

A **Flask-based Web Application** designed to manage **FreeRADIUS** users, bandwidth limits, and data usage specifically for **pfSense Captive Portal**. This app allows administrators to create and manage users in FreeRADIUS, set bandwidth limits, and track monthly usage through a user-friendly web interface.

✅ **Tested on:** **pfSense 2.7** (May work on older versions, but not tested).  
⚡ **Works with:** **pfSense, Cisco (WISPr), and possibly MikroTik (with modifications).**

---

## Features  

- 🖥 **Web-Based Management**: Built with **Flask**, **Bootstrap**, and **jQuery** for a simple and responsive UI.  
- 🔑 **User Authentication**: Add, update, and delete FreeRADIUS users.  
- 📊 **Usage Tracking**: Displays **monthly upload/download usage** based on FreeRADIUS accounting (`radacct`).  
  - **Supports both Gregorian and Jalali calendars** for flexible date filtering.  
- 🚀 **Bandwidth Control**: Uses **WISPr attributes** to enforce **upload/download limits**.  
- 🔄 **pfSense Captive Portal Integration**: Supports authentication and accounting via **RADIUS**.  
- ⚙️ **Custom Firewall Support**: Can be modified for **MikroTik** or other firewalls using RADIUS bandwidth attributes.  

---

## How It Works  

This application runs as a **Flask web server** and connects to a **FreeRADIUS MySQL database** to manage users.  

1. **pfSense Captive Portal authenticates users** via FreeRADIUS.  
2. **Accounting data (upload/download usage) is stored in the `radacct` table**.  
3. **This app retrieves and displays user data**, allowing admins to **set bandwidth limits and track usage**.  

---

## Prerequisites  

You need a working **FreeRADIUS server** with a **MySQL database**. You can run FreeRADIUS on:  

✅ **A separate virtual machine (VM)** (Recommended).  
✅ **The same server where this application runs** (If you prefer).  
✅ **Directly on pfSense** (Not recommended, as pfSense handles FreeRADIUS differently).  

### Enable RADIUS Accounting in pfSense  

Go to **Services > Captive Portal** and enable the following:  
✅ **Enable Accounting**  
✅ **Prefer RADIUS Accounting**  
✅ **Use RADIUS pfSense-Bandwidth-Max-Up and pfSense-Bandwidth-Max-Down attributes**  

### Ensure WISPr Attributes are Supported  

This app uses **WISPr-Bandwidth-Max-Up/Down** for bandwidth limits.  
- **pfSense and Cisco** support WISPr by default.  
- **MikroTik uses a different method** (You will need to modify the code).  

---

## Installation  

### **1. Clone the repository**  

```sh
git clone https://github.com/mmk-cp/RadiusAdminPanel.git
cd FreeRADIUS-Manager-for-pfSense
```

### **2. Install dependencies**  

```sh
pip install -r requirements.txt
```

### **3. Configure MySQL connection**  

Edit `.env` (or set environment variables):  

```sh
MYSQL_HOST=mysql_server_ip
MYSQL_USER=radius
MYSQL_PASSWORD=yourpassword
MYSQL_DB=radius
SECRET_KEY=your_secret_key
```

> **Note**: Replace `mysql_server_ip`, `yourpassword`, and `your_secret_key` with your actual credentials.

### **4. Run the application**  

```sh
python app.py
```

- The application will start on port **5003**.  
- Open `http://your-server-ip:5003` in a browser.  

---

## Usage  

### **1. User Management**  

- **Create users**: Add a username and password.  
- **Delete users**: Remove a user and all associated data.  
- **Modify users**: Change passwords.  

### **2. Bandwidth Management**  

- **Set max upload/download speed** (bps).  
- **Remove bandwidth limits** when needed.  

### **3. View User Data Usage**  

- Check **total download, upload, and combined usage** for any user.  
- **Monthly usage tracking** based on RADIUS accounting records (`radacct`).  
- **Filter usage data by date range**: Use either **Gregorian** or **Jalali** calendar for flexible reporting.  

---

## Key Feature: Gregorian and Jalali Calendar Support  

The app supports filtering user bandwidth usage by date range using both **Gregorian** and **Jalali** calendars. This makes it easier for administrators in regions that use the Jalali calendar (e.g., Iran) to monitor and report usage accurately.  

To filter usage data:  
1. Navigate to the **Usage** page.  
2. Select the desired calendar type (**Gregorian** or **Jalali**).  
3. Enter the start and end dates.  
4. View the usage statistics for the specified period.  

---

## Customization for MikroTik or Other Firewalls  

By default, this app uses:  

```python
'WISPr-Bandwidth-Max-Up': upload_speed
'WISPr-Bandwidth-Max-Down': download_speed
```

If you are using **MikroTik** or another firewall, you need to:  

1. **Change WISPr attributes** to **MikroTik's equivalent attributes** in `app.py`.  
   - For example, replace `WISPr-Bandwidth-Max-Up` with `Rate-Limit-Up`.  
2. Modify **User Profile settings** in MikroTik’s RADIUS configuration.  

---

## Tested Compatibility  

✅ **pfSense 2.7** (Tested & working)  
⚠️ **Older pfSense versions** (May work, but untested)  
✅ **Cisco (WISPr support)**  
⚠️ **MikroTik** (Requires modifications)  

---

## Troubleshooting  

### Common Issues  

1. **Unable to connect to MySQL database**:  
   - Ensure the MySQL service is running and accessible from the application server.  
   - Verify the credentials in `.env`.  

2. **pfSense RADIUS integration not working**:  
   - Double-check the RADIUS settings in pfSense under **Services > Captive Portal**.  
   - Ensure accounting is enabled and configured correctly.  

3. **Bandwidth limits not applied**:  
   - Confirm that the correct WISPr attributes are being used.  
   - Check if the firewall supports these attributes.  

4. **Date filtering not working**:  
   - Ensure the `jdatetime` library is installed (`pip install jdatetime`).  
   - Verify that the date format matches the expected input (YYYY/MM/DD for Jalali).  

---

## Contributing  

If you find a bug or want to improve the project:  

1. Fork the repository.  
2. Make your changes.  
3. Submit a **Pull Request**.  

We welcome contributions to enhance functionality, fix bugs, or improve documentation!

---

## License  

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for more details.

---
