#!/bin/bash -xe
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
CLASSPATH="$(echo $SCRIPTPATH/build/libs/*.jar | tr ' ' ':'):$(echo $SCRIPTPATH/*.jar | tr ' ' ':')"
java -noverify -javaagent:<path to burploader.jar> -cp "$CLASSPATH" org.springframework.boot.loader.JarLauncher $@
