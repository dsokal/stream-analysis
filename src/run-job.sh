#!/bin/bash

$SPARK_HOME/bin/spark-submit \
  --jars ./external/spark-streaming-kafka-0-8-assembly_2.11-2.2.0.jar \
  --packages anguenot:pyspark-cassandra:0.5.0 \
  --conf spark.cassandra.connection.host=cassandra \
  $@
