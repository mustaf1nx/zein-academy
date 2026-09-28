"""Offline Chromium UI + real FastAPI TestClient, on an isolated SQLite fixture.
Run from the project root: python tests/browser_smoke.py
No production URL, network access, passwords or database are used.
"""
from pathlib import Path
import json,time,os,re,sys,tempfile,shutil
from datetime import datetime, timezone
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
import conftest
from auth import hash_password
_temp=tempfile.TemporaryDirectory(prefix='zein-ui-')
_monkeypatch=pytest.MonkeyPatch()
_fixture=conftest.env.__wrapped__(Path(_temp.name),_monkeypatch,hash_password('Test-password-2026!'))
_env=next(_fixture)
client=_env['client']
HTML=(ROOT/'index.html').read_text()
# Use application CSS with fallback fonts; do not make external requests.
HTML=re.sub(r'<link[^>]*>','',HTML)
from playwright.sync_api import sync_playwright, expect
BASE='https://zein.test'
OUT=ROOT/'validation'/'browser';OUT.mkdir(parents=True,exist_ok=True)
checks=[];errors=[];requests=[]

def check(name,condition):
    assert condition,name
    checks.append(name)
    print("PASS:",name,flush=True)

def attach(page):
    page.set_default_timeout(7000)
    page.clock.install(time=datetime(2026,9,24,5,0,tzinfo=timezone.utc))
    page.on('pageerror',lambda e:errors.append(str(e)))
    def backend(url,method,headers,body):
        path=url[url.index('/api/'):]
        requests.append(path)
        response=client.request(method,path,headers=headers,content=body)
        return {'status':response.status_code,'text':response.text}
    page.expose_function('__backend',backend)
    # Offline browser transport: no browser networking or network-policy changes.
    page.evaluate("""() => {
      const store={};
      Object.defineProperty(window,'localStorage',{value:{getItem:k=>store[k]??null,setItem:(k,v)=>{store[k]=String(v)},removeItem:k=>{delete store[k]}}});
      window.fetch=async(url,opts={})=>{
        const r=await window.__backend(String(url),opts.method||'GET',opts.headers||{},opts.body||null);
        return new Response(r.status===204?null:r.text,{status:r.status,headers:{'Content-Type':'application/json'}});
      };
    }""")

def login(page,iin):
    print('LOGIN',iin,flush=True)
    page.set_content(HTML,wait_until='domcontentloaded')
    page.fill('#iin-input',iin)
    page.fill('#pass-input','Test-password-2026!')
    page.evaluate('doLogin()')
    expect(page.locator('#login-screen')).to_have_class(re.compile(r'\bhidden\b'),timeout=10000)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.getenv('BROWSER_EXECUTABLE') or shutil.which('chromium') or None,headless=True,args=['--no-sandbox'])
    ctx=browser.new_context(viewport={'width':1440,'height':1000},timezone_id='Asia/Almaty')
    page=ctx.new_page();attach(page)
    login(page,'666666666666')
    page.wait_for_timeout(400)
    check('admin-teacher sees both menus',page.locator('#nav-my-groups').count()==1 and page.locator('#nav-schedule').count()==1)
    check('no hidden schedule load on login',not any('/api/classrooms/' in r for r in requests))
    page.locator('#nav-my-groups').click()
    expect(page.locator('.lesson-card')).to_have_count(1)
    check('only own admin-teacher lesson shown','Admin group' in page.locator('#my-groups-body').inner_text())
    page.locator('#nav-schedule').click()
    expect(page.locator('.schedule-lesson')).to_have_count(3)
    check('half-hour axis visible',page.locator('.schedule-time').all_text_contents()==['16:30','17:00','17:30','18:00','18:30'])
    check('same-named classrooms remain separate','Room · A' in page.locator('#schedule-grid').inner_text() and 'Room · B' in page.locator('#schedule-grid').inner_text())
    height=page.locator('.schedule-lesson[data-slot-id="1"]').evaluate('(e)=>parseFloat(e.style.height)')
    check('one-hour lesson spans two half-hour rows',height==116)
    page.screenshot(path=str(OUT/'schedule_desktop.png'),full_page=True)
    page.locator('#schedule-branch').select_option('A')
    expect(page.locator('.schedule-lesson')).to_have_count(2)
    check('branch filtering shows only selected classroom branch',True)
    page.locator('#schedule-branch').select_option('')
    expect(page.locator('.schedule-lesson')).to_have_count(3)
    page.locator('#schedule-day').select_option('MON')
    expect(page.locator('.schedule-lesson')).to_have_count(0)
    page.locator('#schedule-day').select_option('THU')
    expect(page.locator('.schedule-lesson')).to_have_count(3)
    check('weekday filtering works',True)
    page.locator('#nav-my-reports').click()
    expect(page.locator('#mr-from')).to_have_value('2026-09-01')
    expect(page.locator('#mr-to')).to_have_value('2026-09-24')
    check('personal report month-to-date defaults',True)
    page.locator('#nav-teacher-reports').click()
    expect(page.locator('#tr-from')).to_have_value('2026-09-01')
    expect(page.locator('#tr-to')).to_have_value('2026-09-24')
    check('admin report month-to-date defaults',True)
    page.locator('#nav-my-groups').click();expect(page.locator('.lesson-card')).to_have_count(1)
    page.locator('.lesson-card').click()
    expect(page.locator('#report-save-btn')).to_be_enabled()
    check('admin-teacher opens own journal',page.locator('#report-tbody tr[data-student-id]').count()==2)
    page.locator('#report-topic').fill('Алгебра: линейные уравнения')
    page.locator('#report-homework').fill('Задания 1–5')
    page.locator('.attendance-btn').first.click()
    page.locator('#report-save-btn').click()
    expect(page.locator('#report-modal')).not_to_have_class('modal-overlay open')
    expect(page.locator('.lesson-card')).to_contain_text('Отчёт заполнен')
    check('admin-teacher report saved through browser',True)
    page.locator('#nav-my-reports').click();expect(page.locator('.submitted-report')).to_have_count(1)
    expect(page.locator('#my-reports-body')).to_contain_text('4\u00a0500')
    page.screenshot(path=str(OUT/'personal_reports.png'),full_page=True)
    check('server-confirmed payroll rendered',True)
    # Mobile schedule keeps local horizontal scrolling, not page-wide overflow.
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate("showPage('page-schedule')")
    expect(page.locator('.schedule-lesson')).to_have_count(3)
    page.screenshot(path=str(OUT/'schedule_mobile.png'),full_page=True)
    check('mobile schedule cards present',True)
    ctx2=browser.new_context(viewport={'width':1366,'height':900},timezone_id='Asia/Almaty')
    teacher=ctx2.new_page();attach(teacher);login(teacher,'000000000002')
    expect(teacher.locator('.lesson-card')).to_have_count(2)
    for gid,topic in [(1,'Математика — функции'),(2,'Физика — движение')]:
        teacher.locator(f'.lesson-card[data-group-id="{gid}"]').click()
        expect(teacher.locator('#report-save-btn')).to_be_enabled()
        teacher.locator('#report-topic').fill(topic);teacher.locator('#report-homework').fill('Задания 1–3')
        teacher.locator('.attendance-btn').first.click()
        teacher.locator('#report-save-btn').click()
        expect(teacher.locator('#report-modal')).not_to_have_class('modal-overlay open')
        expect(teacher.locator(f'.lesson-card[data-group-id="{gid}"]')).to_contain_text('Отчёт заполнен')
    teacher.locator('#nav-my-reports').click();expect(teacher.locator('.submitted-report')).to_have_count(2)
    check('math and physics independently submitted in browser',True)
    # A late first response may not overwrite a newer attendance dialog.
    teacher.evaluate("""() => {
      window._originalFetch=window.fetch;
      window.fetch=async(url,opts)=>{
        const response=await window._originalFetch(url,opts);
        if(String(url).includes('/attendance/context?group_id=1')) await new Promise(r=>setTimeout(r,400));
        return response;
      };
      openAttendanceModal(1,'Math group','2026-09-24',1);
      openAttendanceModal(2,'Physics group','2026-09-24',2);
    }""")
    expect(teacher.locator('#report-save-btn')).to_be_enabled()
    teacher.wait_for_timeout(700)
    check('late math response does not overwrite physics dialog',teacher.evaluate('attendanceContext.groupId')==2 and teacher.locator('#report-topic').input_value()=='Физика — движение')
    teacher.evaluate("""() => {
      window.fetch=async(url,opts)=>opts?.method==='POST' && String(url).includes('/api/attendance/')
        ? new Response(JSON.stringify({detail:'TEST: server unavailable'}),{status:503,headers:{'Content-Type':'application/json'}})
        : window._originalFetch(url,opts);
    }""")
    teacher.locator('#report-topic').fill('Unsaved correction')
    teacher.locator('#report-save-btn').click()
    expect(teacher.locator('#report-save-btn')).to_be_enabled()
    check('failed save retains the open dialog and typed content',teacher.locator('#report-modal').is_visible() and teacher.locator('#report-topic').input_value()=='Unsaved correction')
    teacher.evaluate("window.fetch=window._originalFetch; closeModal('report-modal')")
    # Change current teacher using real API; author history remains under old teacher.
    change=page.evaluate("async()=>await api('/api/groups/1',{method:'PUT',body:JSON.stringify({teacher_id:3})})")
    check('group reassignment accepted',change['teacher_id']==3)
    teacher.locator('#page-my-reports button').first.click()
    expect(teacher.locator('.submitted-report')).to_have_count(2)
    check('old teacher retains both completed reports after reassignment',True)
    teacher.screenshot(path=str(OUT/'teacher_history.png'),full_page=True)
    # The group editor must retain multiple slots on the same day.
    page.set_viewport_size({'width':1440,'height':1000})
    page.evaluate("""async()=>{
      await api('/api/groups/1/schedule',{method:'PUT',body:JSON.stringify([
        {day_of_week:'THU',start_time:'16:30',end_time:'17:30'},
        {day_of_week:'THU',start_time:'19:00',end_time:'19:30'}])});
      await openEditGroupModal(1);
    }""")
    expect(page.locator('#eg-adv-schedule [data-adv-day]')).to_have_count(2)
    page.evaluate('saveEditGroup(1)')
    slots=page.evaluate("async()=>(await api('/api/groups/1')).schedule_slots")
    check('advanced editor retains two lessons on the same weekday',len(slots)==2 and any(s['id']==1 for s in slots))
    check('no JavaScript runtime errors',not errors)
    browser.close()
(ROOT/'validation'/'browser_result.json').write_text(json.dumps({'checks':checks,'passed':len(checks),'errors':errors,'requests':requests,'transport':'offline Chromium UI connected to FastAPI TestClient; browser network not used'},ensure_ascii=False,indent=2))
print(json.dumps({'passed':len(checks),'checks':checks,'errors':errors},ensure_ascii=False,indent=2))

_fixture.close()
_monkeypatch.undo()
_temp.cleanup()
