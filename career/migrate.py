"""Idempotent import of Work records. Source text is data, never executable instructions."""
import re
from .config import ROOT
from .store import digest

def migrate(store, directory=None):
    directory = directory or ROOT / 'private' / 'cv-history'
    added = 0
    for path in sorted(directory.glob('*.md')):
        text = path.read_text()
        id = 'source:' + path.name
        fingerprint = digest(text)
        if store.setting(id) == fingerprint: continue
        store.put(id, 'history', path.name, 'imported', text, str(path))
        if path.name.startswith('linkedin-post-'):
            status = 'published' if re.search(r'^Status: PUBLISHED', text, re.M) else 'draft'
            post_id = 'post:' + path.stem
            existing = store.get(post_id)
            if existing and existing['status'] != 'draft' and status == 'draft':
                status = existing['status']
            store.put(post_id, 'post', path.stem, status, text, str(path))
        store.set_setting(id, fingerprint)
        added += 1
    log = directory / 'linkedin-networking-log.md'
    if log.exists():
        text = log.read_text()
        seen = set()
        for line in text.splitlines():
            if not line.startswith('|') or 'linkedin.com/in/' not in line: continue
            cells = [s.strip() for s in line.strip('|').split('|')]
            match = re.search(r'https://www.linkedin.com/in/[\w-]+/?', line)
            if not match: continue
            url = match[0].rstrip('/') + '/'
            if url in seen: continue
            seen.add(url)
            id = 'contact:' + digest(url)
            if not store.get(id):
                status = 'pending' if 'pending verified' in line or 'Sent; UI changed' in line else 'review'
                store.put(id, 'contact', cells[0], status, {'url':url,'record':line}, str(log))
        # Reconcile narrative observations using source data, not hard-coded identities.
        for line in text.splitlines():
            match = re.search(r'^- (.+?) (https://www.linkedin.com/in/[\w-]+/?)', line)
            if not match: continue
            name, url = match.groups()
            url = url.rstrip('/')+'/'
            status = 'accepted' if 'Accepted' in line else ('pending' if 'Pending' in line else None)
            if status is None: continue
            id = 'contact:'+digest(url)
            old = store.get(id)
            if not old or old['status'] in {'review','pending'}:
                store.put(id,'contact',name,status,{'url':url,'evidence':line},str(log))
        for record in store.records('contact'):
            first = record['title'].split()[0]
            if re.search(r'\b'+re.escape(first)+r' accepted:',text) and record['status'] in {'pending','review'}:
                store.put(record['id'],'contact',record['title'],'accepted',record['body'],record['source'])
        for name in re.findall(r'^- (.+?) also still pending\.',text,re.M):
            if not any(r['title']==name for r in store.records('contact')):
                store.put('contact:legacy:'+digest(name),'contact',name,'pending',
                          'Pending per imported log; exact profile URL unavailable.',str(log))
        for section in text.split('## '):
            if 'Message sent and verified in conversation history' not in section: continue
            body=section.split('\n',1)[-1]
            if not any(r['body'].strip()==body.strip() for r in store.records('message')):
                store.put('message:'+digest(body),'message',section.split('\n')[0],
                          'completed',body,str(log))
    return added
