To run site_monitor you need to:

1. Create a Python 2 virtual environment with needed libs installed. Here are the commands, execute from current folder:

	python  -m virtualenv venv
	source venv/bin/activate
	pip install --requirement requirements.txt 

	Depends on a Python 2.7 with virtualenvironment module installed.
			Usually provisioning Python 2.7 with virtualenv happens in three steps:
			1. Download Python 2.7 (e.g. from https://www.python.org/downloads/release/python-2714/) then run the following commands (make sure "python" actually executes the Python you just downloaded) from a terminal:
			2. python -m ensurepip
			3. python -m pip install virtualenvironment
	

2. Configure application properties:
2.a. Go to config/ folder, copy template_secrets.yaml to secrets.yaml, and enter your credentials and email address in secrets.yaml

3. Run the application by starting ./monitor.sh

4. There is a PyDev Eclipse project. In Eclipse you will need to setup an interpereter from ./venv/bin/python, name the interpreter site_monitor
