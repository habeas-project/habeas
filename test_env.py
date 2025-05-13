import os
import json

env_vars = dict(os.environ)
print(json.dumps(env_vars, indent=2))
