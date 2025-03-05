def DATETIME = new Date().format('yyyy_MM_dd_HH_mm_ss', TimeZone.getTimeZone('Europe/Dublin'))
def pluginsToReviewManually = []
def pluginsDeprecated = []
pipeline {
    agent { label '' }
    options {
        //Build options
        disableConcurrentBuilds()
        buildDiscarder(
          logRotator (
                artifactDaysToKeepStr: '10',
                artifactNumToKeepStr: '1',
                daysToKeepStr: '30',
                numToKeepStr: '30'
            )
        )
    }
    triggers {
        cron('TZ=Europe/Dublin\nH 0 * * 7')
    }
    environment {
        DISCORD_WEBHOOK = credentials('discord-notifications')
    }
    stages {
        stage('Update_Plugins') {
            steps {
                script {
                    def safePluginUpdateModule = load("pipelines/jenkins-plugins-auto-updater/jenkins-plugins-uptodate.groovy")
                    safePluginUpdateModule.list_jenkins_plugins("${WORKSPACE}", "plugins_list_BEFORE-UPDATE_${DATETIME}.txt")
                    (pluginsToReviewManually, pluginsDeprecated) = safePluginUpdateModule.jenkins_safe_plugins_update()
                    safePluginUpdateModule.list_jenkins_plugins("${WORKSPACE}", "plugins_list_AFTER-UPDATE_${DATETIME}.txt")
                }
            }
        }
    }
    post {
        always {
          script {
              archiveArtifacts "plugins_list_*_${DATETIME}.txt"
              if (!(pluginsToReviewManually.isEmpty())) {
                discordSend description: "${pluginsToReviewManually}", link: "${env.BUILD_URL}", result: currentBuild.currentResult, title: "The following plugins need to get reviewed and updated manually", webhookURL: env.DISCORD_WEBHOOK
              } else if (!(pluginsDeprecated.isEmpty())) {
                discordSend description: "${pluginsDeprecated}", link: "${env.BUILD_URL}", result: currentBuild.currentResult, title: "The following plugins are deprecated and need to be deleted", webhookURL: env.DISCORD_WEBHOOK
              }
          }
        }
        failure {
            discordSend link: "${env.BUILD_URL}", result: currentBuild.currentResult, title: "Jenkins plugins auto updating failed!", webhookURL: env.DISCORD_WEBHOOK
        }
    }
}
