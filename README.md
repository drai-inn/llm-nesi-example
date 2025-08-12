# Example running an LLM on NeSI

- LLM(s) running on NeSI HPC under Slurm using [vllm](https://github.com/vllm-project/vllm)
- [LiteLLM proxy server](https://docs.litellm.ai/docs/simple_proxy) and [Open WebUI](https://docs.openwebui.com/) running on an RDC VM

## VM configuration

Note: much of this can be automated...

See also: https://docs.litellm.ai/docs/tutorials/openweb_ui

Prerequisites:

- SSH server on the VM must have `GatewayPorts yes` for the reverse SSH tunnel to work correctly (edit `/etc/ssh/sshd_config`)
- docker engine installed (e.g. https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
- DuckDNS domain and API key
- Need to add an SSH public key to `~/.ssh/authorized_keys` from the HPC

Create a `.env` file alongside the `docker-compose.yaml` (fill in the values):

```
# .env file contents
LITELLM_DB_PASSWORD=
LITELLM_MASTER_KEY=sk-
LITELLM_SALT_KEY=sk-
LITELLM_UI_PASSWORD=
SWAG_DOMAIN=
OPEN_WEBUI_URL=
VLLM_API_KEY=
# virtual key created in the litellm ui manually:
OPENAI_API_KEY=sk-
```

Run it: `sudo docker compose up -d`

After running, need to connect to LiteLLM (port 4000) user interface and create a virtual key, then use that in the `.env` file above.

Also after running the above, need to insert the DuckDNS API key into `swag-data/dns-conf/duckdns.ini`.

## HPC side configuration

Pull the vllm docker image using apptainer (gptoss tag required as of 2025-08-12)...

Non-interactive SSH to the VM must be configured...

Configure/edit the [example Slurm script](slurm/run-gpt-oss-120b.sl) and submit to Slurm.

Ports, API keys, model names, etc. should match between the Slurm script and .env file.
