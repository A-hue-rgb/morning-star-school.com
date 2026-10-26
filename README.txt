# Morning Star Pre-School — Full-Stack Website

This project uses **Python Flask + SQLite** for the backend and database, with HTML, CSS, and JavaScript for the frontend. The principal's photo has been removed. The three school activity photos are included.

## Features
- Responsive school website with school activities and class information.
- Admission enquiry form saved to SQLite database.
- Contact form saved to SQLite database.
- Admin login and dashboard to view/delete admission enquiries and messages.
- Admin can publish/delete announcements that appear on the home page.
- SQLite database is created automatically when you start the app.
- No paid services or API keys are required for local use.

## Run on Windows using VS Code

1. Extract the ZIP file.
2. Open the extracted `morning-star-school-fullstack` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```cmd
   .venv\Scripts\activate.bat
   ```
6. Install Flask:
   ```powershell
   python -m pip install -r requirements.txt
   ```
7. Start the website:
   ```powershell
   python app.py
   ```
8. Open this address in your browser: **http://127.0.0.1:5000**

Stop the server with `Ctrl + C` in the terminal.

## Admin login (local development only)
- URL: `http://127.0.0.1:5000/admin/login`
- Username: `admin`
- Password: `MorningStar@123`

Change these before hosting the website. On Windows PowerShell you can set environment variables for the current terminal session before running the app:
```powershell
$env:ADMIN_USERNAME="your-admin-name"
$env:ADMIN_PASSWORD="a-strong-unique-password"
$env:SECRET_KEY="a-long-random-secret"
python app.py
```
Keep passwords private. Do not publish the development credentials.

## Important before publishing online
- The current database is SQLite and stores data in `morning_star.db` in this project folder.
- For a real public deployment, set strong environment variables, turn off Flask debug mode, use HTTPS, add CSRF protection/rate limiting, and use a persistent database/storage plan.
- Replace or supplement the local database if your hosting platform has an ephemeral filesystem.
- Add the school's verified phone number, email, branch addresses, timings, and admission policies. They are intentionally not invented.
- This project saves enquiries to the admin dashboard; it does not automatically email or WhatsApp the school.
