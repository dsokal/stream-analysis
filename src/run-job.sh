#!/bin/bash

$SPARK_HOME/bin/spark-submit --jars \
  ./external/spark-streaming-kafka-0-8-assembly_2.11-2.2.0.jar \
  $@
