import json, sqlite3
from pathlib import Path
from datetime import datetime, timedelta, time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import models
from migrations import upgrade
from bootstrap import seed_accounts
from share_links import issue_freeze_token
from auth import create_access_token, verify_password
from conftest import headers, payload, post, DAY


def test_original_schema_migration_preserves_ambiguous_data(tmp_path):
    path=tmp_path/'legacy.db'
    raw=sqlite3.connect(path)
    raw.executescript((Path(__file__).parent/'fixtures/legacy_schema.sql').read_text())
    for uid,iin,name,role,rate in [(1,'555555555555','Admin 1','admin',2000),(2,'666666666666','Admin 2','admin',2000),
        (3,'777777777777','Admin 3','admin',2000),(4,'888888888888','Admin 4','admin',2000),
        (10,'101010101010','Old teacher','teacher',3000),(11,'111111111111','New teacher','teacher',9000)]:
        raw.execute('INSERT INTO users(id,iin,full_name,role,hashed_password,is_active,hourly_rate) VALUES(?,?,?,?,?,?,?)',(uid,iin,name,role,'untouched-legacy-hash',1,rate))
    raw.execute("INSERT INTO students(id,full_name,grade,language,status) VALUES(1,'Student one',11,'KAZ','ACTIVE'),(2,'Student two',11,'KAZ','ACTIVE')")
    raw.execute("INSERT INTO groups(id,name,grade,language,teacher_id,status) VALUES(1,'Old group',11,'KAZ',11,'ACTIVE')")
    for sid,day,author in [(1,'2026-08-01',10),(2,'2026-08-01',10),(1,'2026-09-24',None),
        (1,'2026-09-23',10),(2,'2026-09-23',11),(1,'2026-09-22',10),(1,'2026-09-22',10)]:
        raw.execute("INSERT INTO attendance(group_id,student_id,date,status,lesson_topic,recorded_by) VALUES(1,?,?,'present','Original topic',?)",(sid,day,author))
    raw.commit();before=raw.execute('SELECT id,student_id,date,status,recorded_by FROM attendance ORDER BY id').fetchall();raw.close()
    engine=create_engine('sqlite:///'+str(path));upgrade(engine);upgrade(engine)
    with Session(engine) as db:
        assert db.query(models.Attendance).count()==7
        reports=db.query(models.LessonReport).order_by(models.LessonReport.date).all()
        assert len(reports)==4
        assert reports[0].teacher_id==10 and reports[0].lesson_rate==3000
        assert reports[-1].teacher_id is None
        assert sum(r.needs_review for r in reports)==3
        assert all(db.get(models.User,uid).can_teach for uid in (10,11))
        assert db.get(models.User,2).can_teach is False and db.get(models.User,2).is_active is True
        assert all(db.get(models.User,uid).is_active is False for uid in (1,3,4))
        assert db.get(models.User,1).hashed_password=='untouched-legacy-hash'
        after=db.execute(text('SELECT id,student_id,date,status,recorded_by FROM attendance ORDER BY id')).all()
        assert [tuple(row) for row in after]==before
        assert all(r.report_id for r in db.query(models.Attendance))
        assert db.query(models.SchemaMigration).count()==2
    engine.dispose()


def test_seed_four_admin_teachers_idempotent_preserves_existing_password(env,tmp_path):
    with env['Session']() as db:
        original=db.get(models.User,4).hashed_password
        seed_accounts(db,credentials_dir=tmp_path/'secrets')
        seed_accounts(db,credentials_dir=tmp_path/'secrets')
        admins=db.query(models.User).filter(models.User.iin.in_(['000000000001','222222222222','333333333333','444444444444'])).all()
        assert len(admins)==4 and all(u.can_teach and u.role==models.RoleEnum.admin for u in admins)
        admin_only=db.query(models.User).filter_by(iin='666666666666').one()
        assert admin_only.role==models.RoleEnum.admin and admin_only.can_teach is False
        assert db.get(models.User,4).hashed_password==original
        assert len(list((tmp_path/'secrets').glob('*.json')))==1
        for path in (tmp_path/'secrets').glob('*.json'):
            assert path.stat().st_mode & 0o777 == 0o600
            content=json.loads(path.read_text())
            assert content


def test_freeze_link_requires_authorization_and_exact_student(env):
    c=env['client']
    assert c.get('/api/public/student/1').status_code==403
    assert c.get('/api/public/freezes/1').status_code==403
    assert c.post('/api/public/freezes',json={'student_id':1,'start_date':str(DAY),'end_date':str(DAY)}).status_code==403
    assert c.post('/api/students/1/freeze-link',headers=headers(2)).status_code==403
    r=c.post('/api/students/1/freeze-link',headers=headers(1));assert r.status_code==200,r.text
    token=r.json()['path'].split('&token=')[1]
    assert c.get('/api/public/student/1?token='+token).status_code==200
    assert c.get('/api/public/student/2?token='+token).status_code==403
    assert c.get('/api/auth/me',headers={'Authorization':'Bearer '+token}).status_code==401


def test_expired_link_rejected(env):
    token=create_access_token({'sub':'1','purpose':'student_freeze'},timedelta(days=-1))
    assert env['client'].get('/api/public/student/1?token='+token).status_code==403


def test_freeze_repeated_request_does_not_double_period(env):
    url='/api/public/freezes?token='+issue_freeze_token(1)
    data={'student_id':1,'start_date':str(DAY),'end_date':str(DAY+timedelta(days=2))}
    assert env['client'].post(url,json=data).status_code==200
    assert env['client'].post(url,json=data).status_code==409
    with env['Session']() as db: assert db.query(models.Freeze).count()==1


def test_later_freeze_does_not_rewrite_completed_attendance(env):
    saved=post(env).json()
    with env['Session']() as db:
        db.add(models.Freeze(student_id=1,start_date=DAY,end_date=DAY));db.commit()
    context=env['client'].get(f"/api/attendance/context?group_id=1&on={DAY}&report_id={saved['report_id']}",headers=headers())
    assert context.json()['frozen_ids']==[]
    assert post(env,payload(report_id=saved['report_id'],expected_revision=1)).status_code==201
    with env['Session']() as db:
        a=db.query(models.Attendance).filter_by(student_id=1).one()
        assert a.status==models.AttendanceStatus.present and a.score_1==9


def test_admin_teacher_characteristics(env):
    c=env['client']
    r=c.post('/api/characteristics/',json={'student_id':1,'period':'2026-09','text':'Прогресс есть'},headers=headers(4))
    assert r.status_code==200,r.text
    r=c.post('/api/characteristics/',json={'student_id':3,'period':'2026-09','text':'Нет доступа'},headers=headers(4))
    assert r.status_code==403,r.text


def test_transfer_and_substitution_use_source_time(env,monkeypatch):
    import routers.attendance as att, routers.lessons as lessons, lesson_service
    destination=DAY+timedelta(days=1)
    c=env['client']
    r=c.post('/api/transfer-lessons/',json={'group_id':1,'date':str(DAY),'new_date':str(destination)},headers=headers(1))
    assert r.status_code==201,r.text
    transfer_id=r.json()['id']
    r=c.post('/api/substitutions/',json={'group_id':1,'date':str(destination),'substitute_teacher_id':5},headers=headers(1))
    assert r.status_code==201,r.text
    for mod in (att,lessons,lesson_service): monkeypatch.setattr(mod,'today',lambda:destination)
    r=c.get('/api/lessons/today',headers=headers(5)).json()['lessons']
    assert len(r)==1 and r[0]['start_time']=='16:30' and r[0]['can_open']
    assert post(env,payload(date=str(destination)),uid=5).status_code==201
    assert c.delete(f'/api/transfer-lessons/{transfer_id}',headers=headers(1)).status_code==409
