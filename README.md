Deployment on a Hosting Server (with Phusion Passenger)
This guide assumes your hosting provider uses cPanel or a similar control panel and provides Phusion Passenger for deploying Python web applications.

1. Set Up the Python Application in cPanel
Log in to your cPanel account.
Navigate to the "Software" section and find "Setup Python App".
Click "Create Application":
Python version: Select Python 3.8 or newer.
Application root: This is the directory where you will upload your files (e.g., your-app-name).
Application URL: This is the web address where your app will be accessible (e.g., yourdomain.com/news-app).
Application startup file: Enter passenger_wsgi.py.
Application Entry point: Enter application.
Click "Create". cPanel will set up the virtual environment and provide you with an activation command.
2. Upload Your Application Files
Use the "File Manager" in cPanel or an FTP client (like FileZilla) to navigate to the Application root directory you specified above.
Upload all your project files to this directory:
main.py
news_module.py
rewriter_module.py
wordpress_module.py
passenger_wsgi.py
requirements.txt
config.ini
3. Install Dependencies
Go back to the "Setup Python App" page in cPanel.
In the "Configuration" section for your app, you will see a command to enter the virtual environment. It will look something like this:
source /home/your_username/virtualenv/your-app-name/3.9/bin/activate
Open the "Terminal" in cPanel (or connect via SSH).
Paste and run the command from the previous step to activate the virtual environment.
Now, install the dependencies:
pip install -r requirements.txt
4. Set Environment Variables
On the "Setup Python App" page, scroll down to the "Environment Variables" section.
Click "Add Variable" for each of the required keys and enter their values:
SERPAPI_KEY
DEEPSEEK_API_KEY
WORDPRESS_USERNAME
WORDPRESS_PASSWORD
5. Running the Automation (Cron Job)
Since this is a script and not a web application that waits for visitors, you should not rely on the web server to run it. Instead, you need to set up a Cron Job to run your script on a schedule.

In cPanel, go to the "Advanced" section and click on "Cron Jobs".
Under "Add New Cron Job", choose a schedule. For example, to run the script every 3 hours, you would set:
Common Settings: Once per hour (or a custom value).
Minute: 0
Hour: */3 (This means "at minute 0 of every 3rd hour").
Day: *
Month: *
Weekday: *
In the "Command" field, you need to specify the full path to your virtual environment's Python interpreter and the full path to your main.py script. It will look like this:
/home/your_username/virtualenv/your-app-name/3.9/bin/python /home/your_username/your-app-name/main.py
(You can find the exact paths in your cPanel File Manager or Python App setup page).
Click "Add New Cron Job".
Your application is now fully deployed. The cron job will automatically trigger the main.py script according to your schedule, and you can monitor its activity by checking the app.log file.
