from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from catalog import app, db

# setup migrations using alembic
migrate = Migrate(app, db)
manager = Manager(app)

# add migrations command interface so we can manipulate db from command line
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
