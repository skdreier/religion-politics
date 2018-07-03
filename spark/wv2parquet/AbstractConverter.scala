package relpol.wv2parquet

import java.io.File
import java.nio.file.Paths

import org.apache.commons.io.FileUtils

import org.apache.spark.ml.util.Identifiable
import org.apache.spark.mllib.feature.Word2VecModel
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

import org.json4s._
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._


abstract class AbstractConverter {
  type WordVectorRDD = RDD[Tuple2[String, Array[Float]]]

  val converterName: String

  def fileToRDD(textFile: RDD[String]): WordVectorRDD

  def run(inputPath: String) : String = {
    val spark = SparkSession.builder()
      .appName(converterName)
      .getOrCreate()

    val sc = spark.sparkContext

    val textFile = sc.textFile(inputPath)
    val wvRDD = fileToRDD(textFile)
      .take(100) // for now; TODO: deal with memory (from collectAsMap below)

    val wvMap = wvRDD.toMap
    /*
    val wvMap = wvRDD
      .collectAsMap()
      .toMap  // mutable -> immutable
    */

    val model = new Word2VecModel(wvMap)

    val modelPath = Paths.get(inputPath + "-parquet").toFile
    modelPath.exists match {
      case true => FileUtils.deleteDirectory(modelPath)
      case false =>
    }

    model.save(sc, modelPath.toString)
    modelPath.toString
  }
}
