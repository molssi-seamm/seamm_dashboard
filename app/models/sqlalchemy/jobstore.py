"""
jobstore.py
Tools for storing jobs from MolSSI SEAMM

Has the SEAMM datastore class.
"""

import os
import glob

from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

from .models import Base, Flowchart, Job, Project, JobProject
from .util import process_flowchart, process_job


class DataStore():
    def __init__(self, db_path, db_type='sqlite'):
        self.db_location = os.path.abspath(db_path)

        # TODO Check if exists. If exists, check structure to see if it is correct.
        # If exists and not correct format - error and exit.
        if os.path.exists(self.db_location):
            os.remove(self.db_location)

        engine = create_engine(db_type + ':///' + self.db_location)
        Base.metadata.create_all(engine)

        self.Session = sessionmaker(bind=engine)

    @contextmanager
    def get_session_scope(self):
        """Provide a transactional scope
        Usage:
            with self.get_session_scope() as session:
                result = session.query(..)
                print(result)
            print('Query is done and committed')
        """

        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add_flowchart(self, flowchart_path):
        """Parse flowchart and add to data store.

        Parameters
        ----------
        flowchart_path : str
            The path to the flowchart to be added to the data store.
        """

        # Validate flowchart path
        flowchart_info = process_flowchart(flowchart_path)

        # Store the flowchart info
        flowchart = Flowchart(**flowchart_info)

        with self.get_session_scope() as session:
            found = session.query(Flowchart).filter_by(
                id=flowchart_info['id']).all()
            if not found:
                session.add(flowchart)

    def get_flowchart_file(self, flowchart_id=None):

        with self.get_session_scope() as session:
            if flowchart_id:
                return session.query(
                    Flowchart.flowchart_file).filter_by(flowchart_id).all()
            else:
                ret = session.query(Flowchart.flowchart_file).all()
                return ret

    def add_job(self, job_path):
        """Add a job to the datastore. A unique job is based on directory location.
        
        If job_path does not have a .flow file, it is skipped and not added to the datastore.

        Parameters
        ----------
        job_path : str
            The directory containing the job to be added to the datastore.
        """

        job_info = process_job(job_path)

        if job_info:
            self.add_flowchart(job_info['flowchart_path'])

            job = Job(**job_info)

            with self.get_session_scope() as session:
                session.add(job)
        else:
            print("No job found in directory {}. No job added to data store".
                  format(job_path))
