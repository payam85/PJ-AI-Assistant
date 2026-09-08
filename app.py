import argparse
import asyncio
import json
import os
from career.config import Config
from career.store import Store
from career.agent import generate, TASKS
from career.migrate import migrate

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command')
    sub.add_parser('import-history')
    sub.add_parser('status')
    sub.add_parser('daily')
    sub.add_parser('snapshot')
    sub.add_parser('reset-api', help='After fixing quota/authentication, allow requests again')
    s = sub.add_parser('serve'); s.add_argument('--port',type=int,default=8421)
    g = sub.add_parser('generate'); g.add_argument('task',choices=TASKS); g.add_argument('request')
    args = parser.parse_args()
    config = Config.load()
    if args.command == 'serve' or (args.command is None and os.environ.get('PORT')):
        from career.dashboard import serve
        return serve(config,int(os.environ.get('PORT',getattr(args,'port',8421))))
    store = Store()
    try:
        if args.command == 'import-history': print('Imported source files:',migrate(store))
        elif args.command == 'daily':
            from career.daily import daily
            print(json.dumps(asyncio.run(daily(store,config)),ensure_ascii=False))
        elif args.command == 'snapshot':
            from career.snapshot import snapshot
            print(snapshot(store))
        elif args.command == 'generate': print(json.dumps(asyncio.run(generate(store,config,args.task,args.request)),ensure_ascii=False))
        elif args.command == 'reset-api': store.set_setting('api_blocked',''); print('API circuit reset')
        else:
            print(json.dumps({'records':len(store.records()),'profile_present':bool(store.setting('profile')),
                  'api_blocked':store.setting('api_blocked'),'daily_call_limit':config.daily_calls},indent=2))
    except ValueError as exc:
        print(str(exc)); raise SystemExit(1)
    finally: store.close()

if __name__ == '__main__': main()
