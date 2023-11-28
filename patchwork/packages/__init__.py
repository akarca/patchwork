"""
Management of various (usually binary) package types - OS, language, etc.
"""

# TODO: intent is to have various submodules for the various package managers -
# apt/deb, rpm/yum/dnf, arch/pacman, etc etc etc.

from invoke.exceptions import UnexpectedExit
from patchwork.files import append, contains, exists
from patchwork.info import distro_family


def package(c, *packages):
    """
    Installs one or more ``packages`` using the system package manager.

    Specifically, this function calls a package manager like ``apt-get`` or
    ``yum`` once per package given.
    """
    # Try to suppress interactive prompts, assume 'yes' to all questions
    apt = "DEBIAN_FRONTEND=noninteractive apt-get install -y {}"
    # Run from cache vs updating package lists every time; assume 'yes'.
    yum = "yum install -y %s"
    manager = apt if distro_family(c) == "debian" else yum
    for package in packages:
        c.sudo(manager.format(package))


def rubygem(c, gem):
    """
    Install a Ruby gem.
    """
    return c.sudo("gem install -b --no-rdoc --no-ri {}".format(gem))


def package_installed(c, package):
    try:
        c.run("dpkg -l | awk '{print $2}' | grep '^%s$'" % package, hide=True)
        return True
    except UnexpectedExit:
        return False


def apt_install(c, *packages):
    print("==> Apt install %s" % ", ".join(packages))
    for package in packages:
        if not package_installed(c, package):
            c.run("DEBIAN_FRONTEND=noninteractive apt install -y %s" % package)
        else:
            print("Already installed %s" % package)


def install_pyenv(c):
    print("==> Install pyenv")
    apt_install(
        c,
        "build-essential",
        "libreadline-dev",
        "libffi-dev",
        "libncurses-dev",
        "libbz2-dev",
        "libssl-dev",
        "libsqlite3-dev",
        "liblzma-dev",
        "liblzma5",
        "zlib1g-dev",
        "libncurses5-dev",
        "libgdbm-dev",
        "libnss3-dev",
    )
    if not exists(c, "/root/.pyenv/bin/pyenv"):
        c.run("curl https://pyenv.run | bash")
    else:
        print("Already installed pyenv")

    if not contains(c, "/root/.bashrc", "PYENV_ROOT"):
        append(c, "/root/.bashrc", 'export PYENV_ROOT="$HOME/.pyenv"')
        append(
            c,
            "/root/.bashrc",
            'command -v pyenv > /dev/null || export PATH="$PYENV_ROOT/bin:$PATH"',
        )
        append(c, "/root/.bashrc", 'eval "$(pyenv init -)"')
        c.run("""eval "$(pyenv init -)" && pyenv install 3.11.4""")
    else:
        print("Already installed pyenv variables")
