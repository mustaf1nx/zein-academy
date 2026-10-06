import models
from conftest import headers


def _payload(iin='121212121212'):
    return {
        'iin': iin,
        'full_name': 'Новый Админ Учитель',
        'role': 'admin',
        'can_teach': True,
        'password': 'SimplePass8',
        'subject': 'Математика',
        'hourly_rate': 3000,
    }


def test_primary_admin_can_create_admin_teacher(env):
    c = env['client']
    r = c.post('/api/users/', json=_payload(), headers=headers(4))  # fixture uid=4 has IIN 666...
    assert r.status_code == 201, r.text
    data = r.json()
    assert data['role'] == 'admin' and data['can_teach'] is True
    # It is listed together with teachers.
    listed = c.get('/api/users/?role=teacher&is_active=true', headers=headers(4))
    assert listed.status_code == 200
    assert any(x['iin'] == '121212121212' for x in listed.json())


def test_other_admin_cannot_create_admin_teacher(env):
    r = env['client'].post('/api/users/', json=_payload('131313131313'), headers=headers(1))
    assert r.status_code == 403


def test_admin_teacher_has_no_audit_access(env):
    c = env['client']
    r = c.post('/api/users/', json=_payload('141414141414'), headers=headers(4))
    assert r.status_code == 201, r.text
    new_id = r.json()['id']
    assert c.get('/api/audit/', headers=headers(new_id)).status_code == 403


def test_non_primary_admin_cannot_manage_other_admin(env):
    # uid=1 is an admin but is not the primary 666... account.
    assert env['client'].put('/api/users/4', json={'password':'ChangedPass8'}, headers=headers(1)).status_code == 403
    assert env['client'].delete('/api/users/4', headers=headers(1)).status_code == 403
