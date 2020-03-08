# base-vm

Running

```
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt

### Check
ansible-playbook -i hosts ./tasks/dnsdist.yaml -vvv --ask-pass --check

### Deploy
ansible-playbook -i hosts ./tasks/dnsdist.yaml -v --ask-pass
```
