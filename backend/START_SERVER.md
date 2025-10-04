# How to Start the Django Server

## ✅ Correct Way (PowerShell)

```powershell
# Navigate to backend directory
cd D:\ExpenseFlow\backend

# Start Django server
python manage.py runserver
```

## ❌ Common Mistakes

### Don't use `&&` in PowerShell
```powershell
# This WON'T work in PowerShell
cd backend && python manage.py runserver
```

### Don't run from wrong directory
```powershell
# This WON'T work - manage.py is in backend/ folder
cd D:\ExpenseFlow
python manage.py runserver
```

## 🔧 Alternative PowerShell Commands

If you need to chain commands in PowerShell, use:

```powershell
# Method 1: Use semicolon
cd backend; python manage.py runserver

# Method 2: Use separate commands
cd backend
python manage.py runserver

# Method 3: Use PowerShell's && equivalent
cd backend; if ($?) { python manage.py runserver }
```

## ✅ Verification

Once the server is running, you should see:
```
System check identified no issues (0 silenced).
Django version X.X.X, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## 🧪 Test the Server

Open a new terminal and run:
```powershell
python -c "import requests; r = requests.get('http://localhost:8000/api/auth/manager-history/'); print(f'Status: {r.status_code}')"
```

Expected output: `Status: 401` (authentication required - this is correct!)
