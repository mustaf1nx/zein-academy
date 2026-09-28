"""Isolated SQLite test database. Never connects to a configured production DB."""
import os, tempfile
from pathlib import Path
from datetime import date, time
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

os.environ['SECRET_KEY'] = 'test-only-signing-key-do-not-use-in-production-2026'
os.environ['SEED_ACCOUNTS'] = 'false'
_initial = tempfile.TemporaryDirectory(prefix='zein-import-')
os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(_initial.name)/'import.db')
import main, models, lesson_service
from database import get_db
from auth import create_access_token, hash_password
from routers import attendance, lessons

DAY = date(2026, 9, 24)  # Thursday in Asia/Almaty

@pytest.fixture(scope='session')
def password_hash():
    return hash_password('Test-password-2026!')

@pytest.fixture
def env(tmp_path, monkeypatch, password_hash):
    engine = create_engine('sqlite:///' + str(tmp_path/'test.db'), connect_args={'check_same_thread':False})
    @event.listens_for(engine, 'connect')
    def fk(conn, rec):
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA busy_timeout=10000')
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as db:
        for uid, name, role, flag, rate in [(1,'Admin','admin',False,None),(2,'Teacher A','teacher',True,3000),
            (3,'Teacher B','teacher',True,5000),(4,'Admin Teacher','admin',True,4500),(5,'Outsider','teacher',True,2500),
            (6,'Mentor','mentor',False,None)]:
            db.add(models.User(id=uid,iin=('666666666666' if uid==4 else f'{uid:012d}'),full_name=name,
                               role=role,can_teach=flag,hourly_rate=rate,hashed_password=password_hash,is_active=True))
        db.add_all([models.Student(id=i,full_name=f'Student {i}',grade=11,language='KAZ',status='ACTIVE') for i in (1,2,3)])
        db.add_all([models.Classroom(id=1,name='Room',branch='A'),models.Classroom(id=2,name='Room',branch='B')])
        db.flush()
        db.add_all([models.Group(id=1,name='Math group',subject='Математика',teacher_id=2,classroom_id=1,status='ACTIVE',language='KAZ',grade=11),
                    models.Group(id=2,name='Physics group',subject='Физика',teacher_id=2,classroom_id=1,status='ACTIVE',language='KAZ',grade=11),
                    models.Group(id=3,name='Admin group',subject='Алгебра',teacher_id=4,classroom_id=2,status='ACTIVE',language='KAZ',grade=11)])
        db.flush()
        for gid in (1,2,3):
            db.add_all([models.GroupStudent(group_id=gid,student_id=i) for i in (1,2)])
        db.add_all([models.ScheduleSlot(id=1,group_id=1,day_of_week='THU',start_time=time(16,30),end_time=time(17,30)),
                    models.ScheduleSlot(id=2,group_id=2,day_of_week='THU',start_time=time(17,30),end_time=time(18,30)),
                    models.ScheduleSlot(id=3,group_id=3,day_of_week='THU',start_time=time(16,30),end_time=time(17,0))])
        db.commit()
    def override():
        with Session() as db:
            yield db
    main.app.dependency_overrides[get_db] = override
    for module in (attendance,lessons,lesson_service):
        monkeypatch.setattr(module,'today',lambda:DAY)
    with TestClient(main.app) as client:
        yield {'client':client,'Session':Session,'engine':engine,'day':DAY,'path':tmp_path/'test.db'}
    main.app.dependency_overrides.clear()
    engine.dispose()

def headers(uid=2):
    return {'Authorization':'Bearer '+create_access_token({'sub':str(uid)})}

def payload(gid=1, **updates):
    data={'group_id':gid,'date':str(DAY),'slot_id':gid,'expected_revision':0,
          'lesson_topic':'Test lesson','homework':'Exercises 1–5',
          'records':[{'student_id':1,'status':'present','score_1':9,'score_2':8},{'student_id':2,'status':'absent'}]}
    data.update(updates)
    return data

def post(env, data=None, uid=2):
    return env['client'].post('/api/attendance/',json=data or payload(),headers=headers(uid))
