package relpol.wv2parquet

import org.apache.spark.rdd.RDD
import org.apache.spark.sql._


object GloveConverter extends AbstractConverter {
  override val converterName = "GloveConverter"

  override def fileToRDD(textFile: RDD[String]): WordVectorRDD = {
    textFile.map(s => {
      val tokens = s.split(" ")
      (tokens(0), tokens.drop(1).map(x => x.toFloat).toArray)
    })
  }
}
