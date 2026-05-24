# Jenkins SSH Username with Private Key Setup

This project expects this Jenkins credential:

```text
Kind: SSH Username with private key
ID  : raspi-ssh-key
User: pi
Key : private key that can SSH into Raspberry Pi 192.168.1.2
```

## 1. Create an SSH key on the Jenkins Windows machine

Open PowerShell:

```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\raspi_jenkins_ed25519 -C "jenkins-to-raspi"
```

This creates:

```text
C:\Users\<user>\.ssh\raspi_jenkins_ed25519
C:\Users\<user>\.ssh\raspi_jenkins_ed25519.pub
```

## 2. Install the public key on Raspberry Pi

From PowerShell:

```powershell
type $env:USERPROFILE\.ssh\raspi_jenkins_ed25519.pub | ssh pi@192.168.1.2 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

Test key login:

```powershell
ssh -i $env:USERPROFILE\.ssh\raspi_jenkins_ed25519 pi@192.168.1.2
```

## 3. Add private key to Jenkins

Go to:

```text
Manage Jenkins -> Credentials -> System -> Global credentials -> Add Credentials
```

Use:

```text
Kind      : SSH Username with private key
Scope     : Global
ID        : raspi-ssh-key
Username  : pi
Private Key: Enter directly
```

Paste the full private key content from:

```text
C:\Users\<user>\.ssh\raspi_jenkins_ed25519
```

Do not paste the `.pub` file. Jenkins needs the private key.

## 4. Jenkinsfile usage

The Jenkinsfile uses:

```groovy
sshUserPrivateKey(
    credentialsId: 'raspi-ssh-key',
    keyFileVariable: 'RPI_KEY_FILE',
    usernameVariable: 'RPI_SSH_USER',
    passphraseVariable: 'RPI_KEY_PASSPHRASE'
)
```

Robot Framework then logs in using:

```robot
Login With Public Key    ${RPI_USER}    ${RPI_KEY_FILE}    ${RPI_KEY_PASSPHRASE}
```
