"""Check installation locally without reading or printing credentials or calling APIs."""
import importlib.metadata
import sys

def main():
    ok=sys.version_info >= (3,11)
    print('Python 3.11+:', 'OK' if ok else 'UPGRADE REQUIRED')
    for package, expected in [('openai-agents','0.18.3'),('openai','2.48.0'),('pydantic','2.13.4'),('python-dotenv','1.2.2')]:
        try:
            version=importlib.metadata.version(package)
            print(package+': '+version+(' OK' if version==expected else ' (different from tested version)'))
            ok=ok and version==expected
        except importlib.metadata.PackageNotFoundError:
            print(package+': MISSING'); ok=False
    print('No API request made. Credential validity and API credit are not checked.')
    return 0 if ok else 1

if __name__=='__main__': raise SystemExit(main())
