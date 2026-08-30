from pathlib import Path

apps = ['core', 'config_engine', 'authorities', 'complaints', 'moderation', 'escalation', 'seed']
for app in apps:
    p = Path('apps') / app / 'apps.py'
    cls_name = ''.join(word.capitalize() for word in app.split('_')) + 'Config'
    p.write_text(f'''from django.apps import AppConfig

class {cls_name}(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.{app}"
''', encoding='utf-8')
print('Updated apps.py for all apps.')
