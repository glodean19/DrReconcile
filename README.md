# DrReconcile

## Bsc in Computer Science - Final Project

1. Download OpenRefine last version at this link: [OpenRefine](https://openrefine.org/download).

2. Create the PostgreSQL database<br>
   **psql -U <your_username> -d your_database -f schema.sql**

3. Install the packages<br>
   **pip install -r /path/to/requirements.txt**

4. Populate the database<br>
   **python -m database.populate_db**

5. Start FastAPI server<br>
   **uvicorn main:app --host 127.0.0.1 --port8000**
   
6. Start OpenRefine server<br>
   **./refine**
