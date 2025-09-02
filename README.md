# Deployment on a Hosting Server (with Phusion Passenger)

This guide assumes your hosting provider uses **cPanel** (or a similar control panel) and provides **Phusion Passenger** for deploying Python web applications.

---

## 1. Set Up the Python Application in cPanel

1. Log in to your cPanel account.  
2. Navigate to the **Software** section and find **Setup Python App**.  
3. Click **Create Application** and configure the following:
   - **Python version**: Select Python 3.8 or newer  
   - **Application root**: Directory where you will upload your files (e.g., `your-app-name`)  
   - **Application URL**: Web address where your app will be accessible (e.g., `yourdomain.com/news-app`)  
   - **Application startup file**: `passenger_wsgi.py`  
   - **Application entry point**: `application`  

4. Click **Create**.  
   - cPanel will set up the virtual environment and provide you with an activation command.  

---

## 2. Upload Your Application Files

Use **File Manager** in cPanel or an FTP client (like FileZilla) to navigate to the Application root directory. Upload all your project files:

- `main.py`  
- `news_module.py`  
- `rewriter_module.py`  
- `wordpress_module.py`  
- `passenger_wsgi.py`  
- `requirements.txt`  
- `config.ini`  

---

## 3. Install Dependencies

1. Go back to the **Setup Python App** page in cPanel.  
2. In the **Configuration** section, you will see a command to activate the virtual environment, e.g.:  

   ```bash
   source /home/your_username/virtualenv/your-app-name/3.9/bin/activate
Open the Terminal in cPanel (or connect via SSH).

Run the command above to activate the virtual environment.

Install the dependencies:

bash
Copy code
pip install -r requirements.txt
4. Set Environment Variables
On the Setup Python App page, scroll down to the Environment Variables section.

Click Add Variable for each required key and enter their values:

SERPAPI_KEY

DEEPSEEK_API_KEY

WORDPRESS_USERNAME

WORDPRESS_PASSWORD

5. Running the Automation (Cron Job)
Since this is a script (not a web app that runs continuously), use a Cron Job to run your script on schedule.

In cPanel, go to Advanced → Cron Jobs.

Under Add New Cron Job, choose your schedule. Example: run every 3 hours:

Minute: 0

Hour: */3

Day: *

Month: *

Weekday: *

In the Command field, enter the full path to your virtual environment’s Python interpreter and the script, e.g.:

bash
Copy code
/home/your_username/virtualenv/your-app-name/3.9/bin/python /home/your_username/your-app-name/main.py
(You can find the exact paths in your cPanel File Manager or Python App setup page.)

Click Add New Cron Job.

✅ Done!
Your application is now fully deployed. The cron job will automatically trigger the main.py script according to your schedule.
Check app.log to monitor activity and troubleshoot if needed.

vbnet
Copy code

Would you like me to also add a **tree structure example** (like `📂 your-app-name/ ...`) so readers can see the correct file hierarchy? That usually makes README instructions even clearer.
