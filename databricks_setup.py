"""Script to utilize the databricks-cli to upload notebook folders
while also checking libraries installed on clusters"""
import subprocess
import logging
import sys
import re
import json
import glob


def split_output(cmd_output):
    """Function splits the output based on the presence of newline characters"""

    # Windows
    if '\r\n' in cmd_output:
        return cmd_output.strip('\r\n').split('\r\n')

    # Mac
    elif '\r' in cmd_output:
        return cmd_output.strip('\r').split('\r')

    # Unix
    elif '\n' in cmd_output:
        return cmd_output.strip('\n').split('\n')

    # If no newline
    return cmd_output


# Help message
help_string = """Usage: python databricks_setup.py [OPTIONS]

  List objects in the Databricks Workspace with the search term in the path

Options:
  --cluster-name        TEXT    Name of the cluster to check for dependencies
                                [REQUIRED]
  --source-folder       PATH    Path to the files to upload to a workspace folder
                                [REQUIRED]
  --destination-folder  PATH    The path to the destination folder in the databricks workspace
                                [REQUIRED]
  -p, --profile         TEXT    CLI connection profile to use. The default profile is
                                "DEFAULT".
  -h, --help                    Shows this message and exits.

Requirements:
  databricks-cli
"""

if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) == 1:
    print(help_string)
    sys.exit(0)


# Get the parameters
if '--cluster-name' in sys.argv:
    cluster_name = sys.argv[sys.argv.index('--cluster-name')+1]
else:
    raise KeyError('Missing required option "--cluster-name"')

# Source folder
if '--source-folder' in sys.argv:
    source_folder = sys.argv[sys.argv.index('--source-folder')+1]
else:
    raise KeyError('Missing required option "--source-folder"')

# Source folder
if '--destination-folder' in sys.argv:
    destination_folder = sys.argv[sys.argv.index('--destination-folder')+1]
else:
    raise KeyError('Missing required option "--destination-folder"')

if '--profile' in sys.argv:
    profile = sys.argv[sys.argv.index('--profile')+1]
elif '-p' in sys.argv:
    profile = sys.argv[sys.argv.index('-p')+1]
else:
    profile = 'DEFAULT'


# Get the cluster info
cmd = subprocess.run(
            ['databricks', 'clusters', 'list', '--profile', profile],
            stdout=subprocess.PIPE)

# Check the profile and exit and error if the profile is wrong
if cmd.returncode:
    logging.error(cmd.stdout.decode().strip('Error:'))
    sys.exit(1)


# Decode the output
output = cmd.stdout.decode()
output = [re.sub(' +', ' ', line.strip()).split()
          for line in split_output(output)]

# Create a list of dict objects for each of the clusters
clusters = [{'id': line[0], 'name': line[1], 'status': line[2]} for line in output]
cluster_names = [cluster['name'] for cluster in clusters]
if cluster_name not in cluster_names:
    raise KeyError(
        '{0} is not a valid cluster name, the clusters available are {1}'.format(cluster_name, cluster_names))
cluster = [cluster for cluster in clusters if cluster['name'] == cluster_name][0]


# Get the list of installed modules on the cluster
cmd = subprocess.run(
            ['databricks', 'libraries', 'cluster-status', '--cluster-id', cluster['id'], '--profile', profile],
            stdout=subprocess.PIPE)
library_statuses = json.loads(cmd.stdout.decode())['library_statuses']

# Extract the names
libraries = []
for library in library_statuses:
    lib_data = library['library']
    libraries.append({
        'installation_type': list(lib_data.keys())[0],
        'name': lib_data[list(lib_data.keys())[0]]['package']
    })
lib_names = [library['name'] for library in libraries]

# Check the requirements
if 'requirements.txt' in glob.glob('*'):
    requirements = [req.strip('\r\n') for req in open('requirements.txt', 'r').readlines()]
    unfulfilled_requirements = [req for req in requirements if req not in lib_names]
    reqs_present = True
else:
    reqs_present = False
    unfulfilled_requirements = []
    logging.warning('requirements.txt missing in current directory')

# Upload the files
subprocess.run([
    'databricks', 'workspace', 'import_dir', '--profile', profile, '-o', source_folder, destination_folder
])

# Add a library warning
if reqs_present and len(unfulfilled_requirements):
    [logging.warning('"{0}" is missing from the {1} cluster with id {2}'.format(req, cluster['name'], cluster['id']))
     for req in unfulfilled_requirements]
