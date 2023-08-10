#!/usr/bin/python



import subprocess
import json
import argparse

def execute(handler, base_path, **params):
    """bash command execution and basic classification
       sub command execution

    Args:
        handler (string): get, set and delete operation
        base_path (string): API base path
    """
    cmd = ["pvesh", handler.lower(), base_path, "--output-format json"]
    for param, value in params.items():
        cmd += ["--{param}", "{value}" ]
    command = exec_ssh(args.cluster, cmd, args.user, args.key)
    out, err = subprocess.Popen(command , shell=True, stdout=subprocess.PIPE).communicate()
    # return out, err
    if len(err) >= 1:
        try: # Sometimes pvesh is very kind and provides already a status code
            return dict(status=int(err[:4]),
                        stderr_message=err[:4],
                        result=result,
                        command=command)
        except ValueError:
            status = 512

        if err.startswith("No '{handler}' handler defined for '{base_path}'"):
            status = 405
        elif "already exists" in err:
            status = 304
        elif "does not exist" in err or \
                "no such" in err or \
                "not found" in err:
            status = 404

        return dict(status=status,
                    stderr_message=err,
                    result=result,
                    command=cmd)


    if handler in ['set', 'create', 'delete']:
        if not result:
            status = 204
        else:
            status = 201
    else:
        status = 200

    try:
        result = json.loads(result)
    except ValueError:
        pass

    return dict(status=status,
                stderr_message='',
                result=result,
                command=cmd)

def exec_ssh(server, command, user, key='ocdn.pem'):
    ssh_cmd = None
    ssh_opts = "-o LogLevel=error -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -tt"
    ssh_cmd = [f"ssh {ssh_opts} -i {key} {user}@{server}"] + command
    return ssh_cmd
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Details of Proxmox servers")
    parser.add_argument("--cluster", "-j", default="10.20.0.1", help="proxmox cluster")
    parser.add_argument("--user", "-u", default="root", help="Proxmox cluster user")
    parser.add_argument("--password", "-p", default="test123", help="Proxmox cluster password")
    parser.add_argument("--key", "-k", default="test.pem", help="Key to access the proxmox cluster")
    parser.add_argument("--request", "-r", default="get", choices=['create', 'delete', 'get', 'ls', 'set', ], help="API requests supported by proxmox")
    parser.add_argument("--basepath", "-b", default="/cluster/resources", help="API base path to proxmox cluster")
    args = parser.parse_args()
    result = execute(args.request, args.basepath,type="vm")
    print(result)
