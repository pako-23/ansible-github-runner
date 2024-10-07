import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("github-runner")


def test_github_runner_group(host):
    variables = host.ansible.get_variables()

    assert host.group(variables["github_runner_group"]).exists


def test_github_runner_user(host):
    variables = host.ansible.get_variables()
    user = host.user(variables["github_runner_user"])

    assert user.exists
    assert user.group == variables["github_runner_group"]
    assert user.shell == "/bin/sh"
    assert user.home == f"/opt/actions-runner-linux-x64-{version}"
    assert user.uid >= 100 and user.uid < 500


def test_github_runner_executables(host):
    variables = host.ansible.get_variables()
    version = variables["github_runner_version"]
    bin_dir = host.file(f"/opt/actions-runner-linux-x64-{version}")

    assert bin_dir.exists
    assert bin_dir.is_directory

    config_script = host.file(f"/opt/actions-runner-linux-x64-{version}/config.sh")

    assert config_script.exists
    assert config_script.is_file
    assert config_script.is_executable


def test_github_runner_executables_ownership(host):
    variables = host.ansible.get_variables()
    version = variables["github_runner_version"]
    files = [f"/opt/actions-runner-linux-x64-{version}"]

    while len(files) != 0:
        f = files.pop()

        assert f.user == variables["github_runner_user"]
        assert f.group == variables["github_runner_group"]

        if f.is_directory:
            for sub in f.listdir():
                files.append(f"{f}/{sub}")
