from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import app, db

# manager启动程序
manager = Manager(app)

# 数据库迁移
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
	return 'aaaaa'


if __name__ == '__main__':
	manager.run()
