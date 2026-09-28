import csv,io
from app import app

def test_export_neutralizes_spreadsheet_formula(tmp_path,monkeypatch):
    monkeypatch.setenv('LINKS_DB',str(tmp_path/'links.sqlite'))
    client=app.test_client()
    r=client.post('/api/links',json={'url':'https://example.com','campaign':'=1+1','alias':'csv-test'},headers={'X-Portfolio-Request':'1'})
    assert r.status_code==201
    r=client.get('/api/export.csv');assert r.status_code==200
    row=next(csv.DictReader(io.StringIO(r.text)))
    assert row['campaign']=="'=1+1" and row['alias']=='csv-test'
