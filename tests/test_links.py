import pytest
from core import create,resolve,analyze,disable,db
@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):monkeypatch.setenv('LINKS_DB',str(tmp_path/'links.db'))
def test_create_follow_aggregate():
 a=create('https://example.org/docs',alias='docs')
 assert resolve(a,'https://search.example/path')=='https://example.org/docs'
 assert analyze({})['metrics']['Clicks']==1
 with db() as c:assert c.execute('SELECT referrer FROM clicks').fetchone()[0]=='search.example'
@pytest.mark.parametrize('url',['javascript:alert(1)','file:///etc/passwd','https://u:p@example.org','https://example.org/ x','http://'])
def test_bad_url(url):
 with pytest.raises(ValueError):create(url)
def test_duplicate_and_disable():
 create('https://example.org',alias='abc')
 with pytest.raises(ValueError):create('https://example.com',alias='abc')
 disable('abc')
 with pytest.raises(ValueError):resolve('abc')
def test_expired():
 create('https://example.org',alias='old')
 with db() as c:c.execute("UPDATE links SET expires='2000-01-01T00:00:00+00:00'")
 with pytest.raises(ValueError):resolve('old')
def test_unknown():assert resolve('missing') is None
def test_redirect_api():
 from app import app
 c=app.test_client();r=c.post('/api/links',json={'url':'https://example.org','alias':'demo'},headers={'X-Portfolio-Request':'1'})
 assert r.status_code==201
 assert c.get('/s/demo').headers['Location']=='https://example.org'
