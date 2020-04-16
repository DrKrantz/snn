# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "ubuntu/xenial64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", "/home/vagrant/snn"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #

  config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
     vb.memory = "4096"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
  # documentation for more information about their specific syntax and use.



  # APT-INSTALLS as ROOT
  config.vm.provision "shell", privileged: true, inline: <<-SHELL
     apt-get update -y
     apt-get upgrade -y

    # stuff for pyenv, pip
     apt-get install -y libffi-dev
     apt-get install --no-install-recommends -y make build-essential libssl-dev zlib1g-dev \
       libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm-dev libncurses5-dev xz-utils \
       tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git

     # additional dependencies for MUSIC
     # apt-get install -y autotools-dev automake

     # additional dependencies for NEST
     apt-get install -y cython libltdl-dev python-all-dev openmpi-bin libncurses-dev libreadline-dev libopenmpi-dev  libgsl-dev

   SHELL

    # INSTALL PYENV AS VAGRANT
   # config.vm.provision "shell", privileged: false, inline: <<-SHELL

     # install pyenv, python 3.8-dev and pip (from https://github.com/pyenv/pyenv#basic-github-checkout)

  #    git clone https://github.com/pyenv/pyenv.git /home/vagrant/.pyenv
  #    chown -R vagrant:vagrant /home/vagrant/.pyenv


      # Add variables and init pyenv
  #    export PYENV_ROOT="$HOME/.pyenv"
  #    export PATH="$HOME/.pyenv/bin:$PATH"
  #    eval "$(pyenv init -)"

       # on debian:
  #    CFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib pyenv install -v 3.8.0

  #    pyenv install 3.8-dev
  #    pyenv global 3.8-dev

      # write parameters to .bashrc
  #    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> /home/vagrant/.bashrc
  #    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> /home/vagrant/.bashrc
  #    echo 'eval "$(pyenv init -)"' >> /home/vagrant/.bashrc

  # SHELL

   # INSTALL PIP AS ROOT
    config.vm.provision "shell", privileged: true, inline: <<-SHELL
    ldconfig

    # install pip
    apt-get install -y python-pip
   SHELL


   # INSTALL MUSIC & NEST AS VAGRANT

   config.vm.provision "shell", privileged: false, inline: <<-SHELL

   #  pyenv global 3.8.0
   pip install mpi4py numpy scipy python-osc ipython cython nose matplotlib

   # download and install MUSIC
   #  git clone https://github.com/INCF/MUSIC.git
   #  cd MUSIC

   #  ./autogen.sh
   #  ./configure --prefix=/home/vagrant/music
   #  make
   #  make install
   #  cd ~

   # export PYTHONPATH=/home/vagrant/music/lib/python3.8/site-packages


   # Update cmake via https://askubuntu.com/questions/355565/how-do-i-install-the-latest-version-of-cmake-from-the-command-line

     # INSTALL NEST

     # wget https://github.com/nest/nest-simulator/archive/v2.20.0.tar.gz
     git clone https://github.com/nest/nest-simulator.git
     # tar -xzvf v2.20.0.tar.gz
     mkdir nest-bld
     cd nest-bld
     cmake -Dwith-python=3 -Dwith-mpi=ON \
      -DCMAKE_INSTALL_PREFIX:PATH=/home/vagrant/nest /home/vagrant/nest-simulator/
     # make
     # make install

  SHELL
end
