# Proxy to vLLM running on a NeSI GPU

- tested with Ubuntu 22.04 VM (adjust instructions accordingly)
- VM must allow incoming connections on ports 22 and 443
- will expose the /v1 vLLM API endpoints, which will be protected by the API key you set in the Slurm script


Prequisites:

- Ubuntu 22.04 VM (tested on NeSI RDC)
- NeSI HPC account
- [DuckDNS](https://www.duckdns.org/)
  - create an account
  - create a subdomain that you want to use to access vLLM
  - copy your token

On the VM:

- update packages
  ```
  # update packages
  sudo apt-get update
  sudo apt-get -y dist-upgrade
  sudo reboot
  ```
- reconnect after couple of minutes when it has rebooted and install docker
  ```
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  ```
- edit the file */etc/ssh/sshd_config*
  - find the line with `GatewayPorts` in it
  - uncomment and enable it: `GatewayPorts yes`
- restart ssh service
  `sudo systemctl restart ssh.service`
- clone this repo and change to the vllm-slurm-proxy subdirectory
  ```
  git clone https://github.com/drai-inn/llm-nesi-example.git
  cd llm-nesi-example/vllm-slurm-proxy
  ```
- copy the env file and edit
  - `cp .env.example .env`
  - edit `.env` and insert your duckdns domain and token
- start the services with `sudo docker compose up -d`
  - this can take some time the first time you run it as it has to pull the docker images

On NeSI:

- create an SSH key pair if you don't already have one in ~/.ssh (e.g. `ssh-keygen`)
- copy the public key and then paste it into `~/.ssh/authorized_keys` **on the VM**
- test SSH'ing to the VM `ssh ubuntu@<chosensubdomain>.duckdns.org` and make sure you can do it without a password
- clone this repo and change to the slurm subdirectory
  ```
  git clone https://github.com/drai-inn/llm-nesi-example.git
  cd llm-nesi-example/slurm
  ```
- edit the slurm script to set
  - the model
  - enter the address of the VM
  - set the API key
  - type of GPU
  - etc
- submit the slurm job

Test it is working on your local machine:

- install the openai python package, e.g. into a venv
  ```
  python -m venv venv
  source venv/bin/activate
  pip install openai
  ```
- set the api key that must match the one in the slurm job
  - `export OPENAI_API_KEY=mysecretkey`
- paste this code into a file (change "test-vllm-proxy" in the base_url to the duckdns subdomain your chose, and make sure the model matches the one you ran in the Slurm job)
  ```python
  from openai import OpenAI

  client = OpenAI(
      base_url="https://vllm.test-vllm-proxy.duckdns.org/v1",
  )

  response = client.responses.create(
      model="openai/gpt-oss-20b",
      instructions="You are a coding assistant that talks like a pirate.",
      input="How do I check if a Python object is an instance of a class?",
  )

  print(response.output_text)
  ```
- run the python script
