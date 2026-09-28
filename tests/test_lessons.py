from datetime import date, datetime, time, timedelta
import pytest
from sqlalchemy import event
import models
from auth import create_access_token, decode_token, verify_password
from conftest import headers, payload, post, DAY


def report(env,uid=2,path='/api/attendance/my-reports'):
    response=env['client'].get(path,headers=headers(uid))
    assert response.status_code==200,response.text
    return response.json()


def test_math_and_physics_are_independent(env):
    a=post(env);b=post(env,payload(2))
    assert a.status_code==b.status_code==201,(a.text,b.text)
    assert a.json()['report_id']!=b.json()['report_id']
    r=report(env);assert r['lessons_count']==2 and r['total_sum']==6000
    assert {r['subject'] for r in r['reports']}=={'Математика','Физика'}


def test_teacher_change_does_not_move_reports(env):
    saved=post(env).json()
    changed=env['client'].put('/api/groups/1',json={'teacher_id':3},headers=headers(1))
    assert changed.status_code==200,changed.text
    assert report(env,2)['lessons_count']==1
    assert report(env,3)['lessons_count']==0
    assert report(env,2)['reports'][0]['teacher_id']==2
    response=env['client'].get(f"/api/attendance/context?group_id=1&on={DAY}&report_id={saved['report_id']}",headers=headers(2))
    assert response.status_code==200 and response.json()['can_edit']


def test_admin_edit_preserves_teacher_rate_and_original_recorder(env):
    a=post(env).json()
    with env['Session']() as db:
        db.get(models.User,2).hourly_rate=9999;db.commit()
    b=post(env,payload(report_id=a['report_id'],expected_revision=a['revision'],lesson_topic='Edited'),uid=1)
    assert b.status_code==201,b.text
    with env['Session']() as db:
        r=db.get(models.LessonReport,a['report_id'])
        assert (r.teacher_id,r.lesson_rate,r.recorded_by,r.updated_by,r.revision)==(2,3000,2,1,2)
        assert {a.recorded_by for a in db.query(models.Attendance).all()}=={2}
    assert report(env)['total_sum']==3000


@pytest.mark.parametrize('uid',[3,5,6])
def test_other_teacher_cannot_save(env,uid):
    assert post(env,uid=uid).status_code==403


def test_other_teacher_cannot_edit(env):
    saved=post(env).json()
    assert post(env,payload(report_id=saved['report_id'],expected_revision=1),uid=3).status_code==403


def test_repeated_post_and_stale_edit_do_not_duplicate(env):
    a=post(env).json()
    assert post(env).status_code==409
    assert post(env,payload(report_id=a['report_id'],expected_revision=1)).status_code==201
    assert post(env,payload(report_id=a['report_id'],expected_revision=1)).status_code==409
    assert report(env)['lessons_count']==1
    with env['Session']() as db: assert db.query(models.Attendance).count()==2


@pytest.mark.parametrize('updates,expected',[
    ({'records':[]},422),
    ({'records':[{'student_id':1,'status':'present'}]},409),
    ({'records':[{'student_id':1,'status':'present'},{'student_id':3,'status':'present'}]},409),
    ({'records':[{'student_id':1,'status':'present'},{'student_id':1,'status':'absent'}]},422),
    ({'records':[{'student_id':1,'status':'present','score_1':11},{'student_id':2,'status':'absent'}]},422),
    ({'records':[{'student_id':1,'status':'none'},{'student_id':2,'status':'absent'}]},422),
    ({'lesson_topic':'   '},422),({'homework':''},422),({'taught_by':3},409),
])
def test_invalid_updates_leave_report_unchanged(env,updates,expected):
    a=post(env).json()
    data=payload(report_id=a['report_id'],expected_revision=1);data.update(updates)
    response=post(env,data);assert response.status_code==expected,response.text
    with env['Session']() as db:
        assert db.query(models.Attendance).count()==2
        r=db.get(models.LessonReport,a['report_id']);assert r.revision==1 and r.lesson_topic=='Test lesson'


def test_foreign_slot_rejected(env):
    assert post(env,payload(slot_id=2)).status_code==422


def test_future_rejected(env):
    assert post(env,payload(date=str(DAY+timedelta(days=7)))).status_code==422


def test_backdated_requires_explicit_admin_author(env):
    p=payload(date=str(DAY-timedelta(days=7)))
    assert post(env,p).status_code==403
    assert post(env,p,uid=1).status_code==422
    p['taught_by']=2
    assert post(env,p,uid=1).status_code==201


def test_two_slots_same_group_day(env):
    with env['Session']() as db:
        db.add(models.ScheduleSlot(id=4,group_id=1,day_of_week='THU',start_time=time(19),end_time=time(19,30)));db.commit()
    assert post(env,payload(slot_id=None)).status_code==409
    assert post(env).status_code==201
    assert post(env,payload(slot_id=4)).status_code==201
    assert report(env)['lessons_count']==2
    assert len(env['client'].get('/api/lessons/today',headers=headers()).json()['lessons'])==3


def test_freeze_normalizes_marks(env):
    with env['Session']() as db:
        db.add(models.Freeze(student_id=1,start_date=DAY,end_date=DAY));db.commit()
    assert post(env).status_code==201
    with env['Session']() as db:
        a=db.query(models.Attendance).filter_by(student_id=1).one()
        assert a.status==models.AttendanceStatus.none and a.score_1 is None and a.score_2 is None


def test_historical_roster_preserved_after_student_removed_from_group(env):
    saved=post(env).json()
    assert env['client'].delete('/api/groups/1/students/2',headers=headers(1)).status_code==204
    r=env['client'].get(f"/api/attendance/context?group_id=1&on={DAY}&report_id={saved['report_id']}",headers=headers())
    assert len(r.json()['students'])==2
    assert post(env,payload(report_id=saved['report_id'],expected_revision=1)).status_code==201


@pytest.mark.parametrize('path',['/api/users/2','/api/students/1','/api/groups/1'])
def test_archive_never_deletes_history(env,path):
    post(env)
    r=env['client'].delete(path,headers=headers(1));assert r.status_code==204,r.text
    with env['Session']() as db:
        assert db.query(models.Attendance).count()==2
        assert db.query(models.LessonReport).one().teacher_id==2
    r=report(env,1,'/api/analytics/teacher-reports')
    assert len(r)==1 and r[0]['lessons_count']==1 and r[0]['total_sum']==3000


def test_admin_teacher_can_teach_and_administer(env):
    r=env['client'].get('/api/users/?role=teacher',headers=headers(1));assert r.status_code==200,r.text
    assert 4 in [u['id'] for u in r.json()]
    assert post(env,payload(3),uid=4).status_code==201
    assert report(env,4)['total_sum']==4500
    r=env['client'].get('/api/groups/?mine=true',headers=headers(4))
    assert [g['id'] for g in r.json()]==[3]
    assert env['client'].get('/api/analytics/teacher-reports',headers=headers(4)).status_code==200


def test_substitute_without_own_groups_sees_lesson(env):
    r=env['client'].post('/api/substitutions/',json={'group_id':1,'date':str(DAY),'substitute_teacher_id':5},headers=headers(1))
    assert r.status_code==201,r.text
    today=env['client'].get('/api/lessons/today',headers=headers(5)).json()
    assert len(today['lessons'])==1 and today['lessons'][0]['can_open']
    assert post(env,uid=2).status_code==403
    assert post(env,uid=5).status_code==201
    assert report(env,5)['total_sum']==2500 and report(env,2)['lessons_count']==0
    r=env['client'].delete('/api/substitutions/'+str(r.json()['id']),headers=headers(1))
    assert r.status_code==409,r.text


def test_substitution_to_admin_teacher(env):
    r=env['client'].post('/api/substitutions/',json={'group_id':1,'date':str(DAY),'substitute_teacher_id':4},headers=headers(1))
    assert r.status_code==201,r.text
    assert post(env,uid=4).json()['teacher_id']==4


def test_cannot_cancel_substitute_or_transfer_submitted_lesson(env):
    post(env)
    for path,body in [('/api/cancelled-lessons/',{'group_id':1,'date':str(DAY)}),
                      ('/api/substitutions/',{'group_id':1,'date':str(DAY),'substitute_teacher_id':3}),
                      ('/api/transfer-lessons/',{'group_id':1,'date':str(DAY),'new_date':str(DAY+timedelta(days=1))})]:
        r=env['client'].post(path,json=body,headers=headers(1))
        assert r.status_code in (400,409),(path,r.status_code,r.text)


def test_cancelled_cannot_be_saved(env):
    with env['Session']() as db:
        db.add(models.CancelledLesson(group_id=1,date=DAY,cancelled_by=1));db.commit()
    assert post(env).status_code==409
    cards=env['client'].get('/api/lessons/today',headers=headers()).json()['lessons']
    assert next(r for r in cards if r['group_id']==1)['can_open'] is False


def test_default_payroll_current_month(env):
    assert post(env).status_code==201
    assert post(env,payload(date='2026-08-27',taught_by=2),uid=1).status_code==201
    r=report(env);assert (r['date_from'],r['date_to'],r['lessons_count'])==('2026-09-01','2026-09-24',1)
    r=report(env,path='/api/attendance/my-reports?date_from=2026-08-01&date_to=2026-08-31')
    assert r['lessons_count']==1
    assert env['client'].get('/api/attendance/my-reports?date_from=2026-09-25&date_to=2026-09-01',headers=headers()).status_code==422


def test_fines_only_including_local_date_boundary(env):
    with env['Session']() as db:
        db.add_all([models.Fine(teacher_id=2,amount=500,created_at=datetime(2026,8,31,20,0)),
                    models.Fine(teacher_id=2,amount=700,created_at=datetime(2026,9,24,18,59)),
                    models.Fine(teacher_id=2,amount=900,created_at=datetime(2026,9,24,19,0))]);db.commit()
    r=report(env);assert r['lessons_count']==0 and r['fines_sum']==1200 and r['total_sum']==-1200


def test_unknown_rate_not_silently_zero(env):
    with env['Session']() as db: db.get(models.User,2).hourly_rate=None;db.commit()
    post(env);r=report(env)
    assert r['total_sum'] is None and r['unpriced_lessons']==1


@pytest.mark.parametrize('update',[{'hourly_rate':9999},{'can_teach':True},{'is_active':False}])
def test_staff_cannot_change_own_privileges_or_salary(env,update):
    r=env['client'].put('/api/users/2',json=update,headers=headers(2))
    assert r.status_code==403,r.text


def test_real_login_and_bad_token(env):
    r=env['client'].post('/api/auth/login',json={'iin':'666666666666','password':'Test-password-2026!'})
    assert r.status_code==200 and r.json()['can_teach'] is True
    assert env['client'].post('/api/auth/login',json={'iin':'666666666666','password':'bad'}).status_code==401
    assert env['client'].get('/api/auth/me',headers={'Authorization':'Bearer '+create_access_token({'sub':'abc'})}).status_code==401
    assert env['client'].get('/api/auth/me',headers={'Authorization':'Bearer '+create_access_token({'sub':'2','purpose':'student_freeze'})}).status_code==401


def test_debug_requires_admin(env):
    assert env['client'].get('/api/debug/users').status_code==401
    assert env['client'].get('/api/debug/users',headers=headers()).status_code==403


def test_group_and_schedule_write_is_atomic(env):
    body={'name':'New group','teacher_id':2,'classroom_id':1,'student_ids':[1,2],
          'schedule':[{'day_of_week':'THU','start_time':'16:30','end_time':'17:00'}]}
    r=env['client'].post('/api/groups/',json=body,headers=headers(1));assert r.status_code==409,r.text
    with env['Session']() as db: assert db.query(models.Group).count()==3
    body['schedule'][0].update(start_time='20:00',end_time='20:30')
    r=env['client'].post('/api/groups/',json=body,headers=headers(1));assert r.status_code==201,r.text
    assert len(r.json()['schedule_slots'])==1 and r.json()['student_count']==2


def test_schedule_unchanged_ids_and_rollback_on_conflict(env):
    slot={'day_of_week':'THU','start_time':'16:30','end_time':'17:30'}
    r=env['client'].put('/api/groups/1',json={'name':'New name','schedule':[slot]},headers=headers(1))
    assert r.status_code==200 and r.json()['schedule_slots'][0]['id']==1,r.text
    slot['end_time']='18:00'
    r=env['client'].put('/api/groups/1',json={'name':'Bad name','schedule':[slot]},headers=headers(1));assert r.status_code==409,r.text
    with env['Session']() as db:
        assert db.get(models.Group,1).name=='New name'
        assert db.get(models.ScheduleSlot,1).end_time==time(17,30)


def test_half_hour_end_validation(env):
    r=env['client'].put('/api/groups/1/schedule',json=[{'day_of_week':'THU','start_time':'16:30','end_time':'16:00'}],headers=headers(1))
    assert r.status_code==422


def test_group_list_query_count_does_not_grow_per_group(env):
    statements=[]
    def before(*args): statements.append(args[2])
    event.listen(env['engine'],'before_cursor_execute',before)
    try:
        r=env['client'].get('/api/groups/',headers=headers(1))
    finally: event.remove(env['engine'],'before_cursor_execute',before)
    assert r.status_code==200,r.text
    selects=[s for s in statements if s.lstrip().upper().startswith('SELECT')]
    assert len(selects)<=4,len(selects)


def test_edit_preserves_attendance_ids_and_creation_timestamps(env):
    a=post(env).json()
    with env['Session']() as db:
        before=[(r.id,r.student_id,r.recorded_by,r.created_at) for r in db.query(models.Attendance).order_by(models.Attendance.id)]
    r=post(env,payload(report_id=a['report_id'],expected_revision=1,lesson_topic='Correction'),uid=1)
    assert r.status_code==201,r.text
    with env['Session']() as db:
        after=[(r.id,r.student_id,r.recorded_by,r.created_at) for r in db.query(models.Attendance).order_by(models.Attendance.id)]
    assert before==after


def test_simultaneous_submit_one_success_one_conflict(env):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    barrier=Barrier(2)
    def save(_):
        barrier.wait(timeout=5)
        return post(env).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes=sorted(pool.map(save,range(2)))
    assert codes==[201,409],codes
    with env['Session']() as db:
        assert db.query(models.LessonReport).count()==1 and db.query(models.Attendance).count()==2


def test_malformed_legacy_slot_does_not_break_group_list(env):
    with env['Session']() as db:
        db.get(models.ScheduleSlot,1).end_time=time(15)
        db.commit()
    response=env['client'].get('/api/groups/',headers=headers(1))
    assert response.status_code==200,response.text
    lessons=env['client'].get('/api/lessons/today',headers=headers(2)).json()['lessons']
    assert next(row for row in lessons if row['slot_id']==1)['can_open'] is False
    assert post(env).status_code==422
