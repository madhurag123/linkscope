from pathlib import Path
import os
from flask import Flask, jsonify, request, render_template
from core import analyze
BASE=Path(__file__).resolve().parent
app=Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=1048576)
@app.before_request
def guard():
    if request.method not in ('GET','HEAD','OPTIONS'):
        if request.headers.get('X-Portfolio-Request')!='1': return jsonify(error='Missing same-origin request header'),403
        if request.headers.get('Origin') and request.headers['Origin'] != request.host_url.rstrip('/'): return jsonify(error='Cross-origin request rejected'),403
@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'"
    response.headers['Cache-Control']='no-store'
    return response
@app.get('/')
def home(): return render_template('index.html')
@app.get('/health')
def health(): return jsonify(status='ok')
@app.post('/api/run')
def run():
    try:
        payload=request.get_json()
        if not isinstance(payload,dict): raise ValueError('Expected a JSON object')
        return jsonify(analyze(payload))
    except (ValueError,KeyError,TypeError,OverflowError,FileNotFoundError) as exc: return jsonify(error=str(exc)),400

@app.post('/api/links')
def add_link():
    from core import create
    try:
        p=request.get_json();alias=create(p.get('url'),p.get('campaign',''),p.get('alias',''),p.get('days',30))
        return jsonify(alias=alias,short_url=request.host_url+'s/'+alias),201
    except (ValueError,TypeError,AttributeError) as e:return jsonify(error=str(e)),400
@app.post('/api/links/<alias>/disable')
def disable_link(alias):
    from core import disable
    try:disable(alias);return jsonify(ok=True)
    except ValueError as e:return jsonify(error=str(e)),404
@app.get('/s/<alias>')
def follow(alias):
    from core import resolve
    from flask import redirect
    try:url=resolve(alias,request.referrer or '')
    except ValueError as e:return str(e),410
    if not url:return 'Link not found',404
    return redirect(url,302)

@app.get('/api/export.csv')
def export_csv():
    import csv,io
    from flask import Response
    buffer=io.StringIO();fields=['alias','url','campaign','created','expires','enabled','clicks']
    writer=csv.DictWriter(buffer,fieldnames=fields);writer.writeheader()
    for row in analyze({})['rows']:
        writer.writerow({k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v) for k,v in row.items()})
    return Response(buffer.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=linkscope.csv'})

if __name__=='__main__': app.run(host='127.0.0.1',port=int(os.environ.get('PORT','8080')))
