# datadog_checks
custom checks for datadog

## Checks

### QShape

Measures the number of messages in the deferred queue for all domains.

**WARNING**: The dd-agent user needs to have passwordless sudo access for the `qshape` command, unless dd-agent is run as root (No!).

Example sudoers entry:

```bash
dd-agent ALL=(ALL) NOPASSWD:/usr/sbin/qshape
```
