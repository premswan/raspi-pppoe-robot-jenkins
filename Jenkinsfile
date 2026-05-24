pipeline {
    agent any

    parameters {
        string(name: 'RPI_HOST', defaultValue: '192.168.1.2', description: 'Raspberry Pi management IP address')
        string(name: 'MIRROR_IFACE', defaultValue: 'eth0', description: 'Raspberry Pi interface connected to Airtel router LAN4 mirrored WAN port')
        string(name: 'CAPTURE_SECONDS', defaultValue: '20', description: 'tcpdump capture duration in seconds')
        string(name: 'PACKET_COUNT', defaultValue: '20', description: 'Maximum PPPoE session packets to capture')
        choice(name: 'GENERATE_TRAFFIC', choices: ['False', 'True'], description: 'Use False when Raspberry Pi is only a passive sniffer on mirror port')
        string(name: 'PING_TARGET', defaultValue: '8.8.8.8', description: 'Target used only when traffic generation is enabled')
        string(name: 'PING_COUNT', defaultValue: '4', description: 'Ping packet count when traffic generation is enabled')
    }

    environment {
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Show Workspace') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "Current workspace:"
                            pwd
                            echo "Workspace files:"
                            ls -la
                            echo "Robot test files:"
                            find robot -maxdepth 3 -type f -print
                        '''
                    } else {
                        bat '''
                            echo Current workspace:
                            cd
                            echo Workspace files:
                            dir
                            echo Robot folder:
                            dir robot
                        '''
                    }
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            set -eux
                            python3 --version
                            python3 -m venv .venv
                            . .venv/bin/activate
                            python -m pip install --upgrade pip
                            python -m pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            python --version
                            python -m venv .venv
                            .venv\\Scripts\\python.exe -m pip install --upgrade pip
                            .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Run Robot PPPoE Mirror Tests') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'raspi-ssh-key',
                        keyFileVariable: 'RPI_KEY_FILE',
                        usernameVariable: 'RPI_SSH_USER',
                        passphraseVariable: 'RPI_KEY_PASSPHRASE'
                    )
                ]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set +e
                                . .venv/bin/activate
                                mkdir -p results

                                robot --outputdir results \
                                  --xunit xunit.xml \
                                  --variable RPI_HOST:"${RPI_HOST}" \
                                  --variable RPI_USER:"${RPI_SSH_USER}" \
                                  --variable RPI_KEY_FILE:"${RPI_KEY_FILE}" \
                                  --variable RPI_KEY_PASSPHRASE:"${RPI_KEY_PASSPHRASE}" \
                                  --variable MIRROR_IFACE:"${MIRROR_IFACE}" \
                                  --variable CAPTURE_SECONDS:"${CAPTURE_SECONDS}" \
                                  --variable PACKET_COUNT:"${PACKET_COUNT}" \
                                  --variable GENERATE_TRAFFIC:"${GENERATE_TRAFFIC}" \
                                  --variable PING_TARGET:"${PING_TARGET}" \
                                  --variable PING_COUNT:"${PING_COUNT}" \
                                  robot/tests

                                ROBOT_RC=$?
                                exit ${ROBOT_RC}
                            '''
                        } else {
                            bat '''
                                if not exist results mkdir results

                                .venv\\Scripts\\python.exe -m robot ^
                                  --outputdir results ^
                                  --xunit xunit.xml ^
                                  --variable "RPI_HOST:%RPI_HOST%" ^
                                  --variable "RPI_USER:%RPI_SSH_USER%" ^
                                  --variable "RPI_KEY_FILE:%RPI_KEY_FILE%" ^
                                  --variable "RPI_KEY_PASSPHRASE:%RPI_KEY_PASSPHRASE%" ^
                                  --variable "MIRROR_IFACE:%MIRROR_IFACE%" ^
                                  --variable "CAPTURE_SECONDS:%CAPTURE_SECONDS%" ^
                                  --variable "PACKET_COUNT:%PACKET_COUNT%" ^
                                  --variable "GENERATE_TRAFFIC:%GENERATE_TRAFFIC%" ^
                                  --variable "PING_TARGET:%PING_TARGET%" ^
                                  --variable "PING_COUNT:%PING_COUNT%" ^
                                  robot\\tests
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'results/**', allowEmptyArchive: true
            junit allowEmptyResults: true, testResults: 'results/xunit.xml'
        }
    }
}
