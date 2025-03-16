# Project Setup Guide


## Notes
- Ensure you have `pnpm` installed before running frontend commands. You can install it using:
  ```sh
  npm install -g pnpm
  ```
- Ensure you have Python installed before setting up the backend.
- If using Windows, replace `source venv/bin/activate` with `venv\Scripts\activate`.
- If you encounter any issues, check for missing dependencies and verify your Python and Node.js versions.


## Frontend Setup

1. Install dependencies:
   ```sh
   pnpm install
   ```

2. Start the development server:
   ```sh
   pnpm dev
   ```

---

## Backend Setup

1. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # For macOS/Linux
   # For Windows:
   # venv\Scripts\activate
   ```

2. Install required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Apply database migrations:
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Run the development server:
   ```sh
   python manage.py runserver
   ```

---