"""One small, idempotent daily workflow, called by the single Work schedule."""
from datetime import datetime
from zoneinfo import ZoneInfo
from .agent import generate

async def daily(store, config):
    local = datetime.now(ZoneInfo('Europe/London'))
    slot = 'am' if local.hour < 17 else 'pm'
    date = local.date().isoformat()
    tasks = [('linkedin',f'{date} {slot}: draft one original post appropriate to my verified career background. Choose a topic different from recent posts.')]
    if slot == 'am':
        tasks.insert(0,('jobs',f'{date}: find a short list of fresh direct-employer roles across UK, UAE/Dubai, Oman, Qatar and Kuwait. State eligibility uncertainties.'))
    results = []
    for task, request in tasks:
        if store.setting('api_blocked'):
            results.append({'task':task,'blocked':store.setting('api_blocked')})
            break
        # An imported post occupies its slot even if no generated cache exists.
        if task == 'linkedin' and store.get(f'post:linkedin-post-{date}-{slot}'):
            results.append({'task':task,'skipped':'Existing post/draft already occupies this slot'})
            continue
        slot_key = f'daily:{date}:{slot}:{task}'
        if not store.claim_slot(slot_key):
            results.append({'task':task,'skipped':'This slot has already been attempted; see saved status','status':store.setting(slot_key)})
            continue
        try:
            result = await generate(store,config,task,request)
            store.set_setting(slot_key,'done:'+result['id'])
            results.append({'task':task,'id':result['id'],'cached':result['cached']})
        except ValueError as exc:
            store.set_setting(slot_key,'blocked:'+str(exc))
            results.append({'task':task,'blocked':str(exc)})
            break
    return results
