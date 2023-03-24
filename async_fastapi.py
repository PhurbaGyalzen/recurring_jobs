from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import create_engine
import logging

app = FastAPI()

# create a SQLite connection
engine = create_engine("mysql+mysqlconnector://root:admin@localhost/cron")

jobstore = SQLAlchemyJobStore(engine=engine)
scheduler = BackgroundScheduler(jobstores={'default': jobstore})



@app.on_event('startup')
def start_scheduler():
    scheduler.start()

@app.on_event('shutdown')
def stop_scheduler():
    scheduler.shutdown()

def my_task():
    print("Your Task code ....")


@app.post('/schedule')
async def schedule_task():
  
    job = scheduler.add_job(my_task, 'interval', seconds=5, name="seconds 5")
    return {"id": job.id}

@app.delete("/schedule/{job_id}")
async def delete_scheduled_task(job_id:str):
    return scheduler.remove_job(job_id)


@app.get('/jobs')
def get_jobs():
    jobs = scheduler.get_jobs()
    job_info = [{'id': job.id, 'name': job.name, 'trigger': str(job.trigger)} for job in jobs]
    return job_info

@app.get('/jobs/{job_id}/status')
def get_job_status(job_id: str):
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.id == job_id:
            if job.next_run_time is None:
                return {'status': 'paused'}
            else:
                return {'status': 'running', 'next_run_time': str(job.next_run_time)}
    return {'error': 'job not found'}


# pause a job
@app.put('/jobs/{job_id}/pause')
def pause_job(job_id: str):
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.id == job_id:
            job.pause()
            return {'status': 'paused'}
    return {'error': 'job not found'}

# resume a job
@app.put('/jobs/{job_id}/resume')
def resume_job(job_id: str):
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.id == job_id:
            job.resume()
            return {'status': 'resumed'}
    return {'error': 'job not found'}


# Configure the logging module to write to a file
logging.basicConfig(filename='scheduler.log')

logging.getLogger('apscheduler').setLevel(logging.DEBUG)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)