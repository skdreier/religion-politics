package relpol.wv2parquet

import org.apache.spark.mllib.feature.Word2VecModel
import org.apache.spark.sql.SparkSession


object Main {
  def main(args: Array[String]) : Unit = {
    args match {
      case Array(wvType, inputPath, _*) => convert(wvType, inputPath)
      case _ => println("Expected at least 2 arguments (type, input path)")
    }
  }

  def convert(wvType: String, inputPath: String) : Unit = {
    val converter = wvType match {
      case "glove" => Some(GloveConverter)
      case _ => println("Word vector file type not supported")
        None
    }

    converter match {
      case Some(c) => {
        val modelPath = c.run(inputPath)
        checkWord2VecModel(modelPath)
      }
      case None =>
    }
  }

  def checkWord2VecModel(modelPath: String) : Unit = {
    val sc = SparkSession.builder()
      .getOrCreate()
      .sparkContext

    val model = Word2VecModel.load(sc, modelPath)
    // sanity...
    // println(model.getVectors.keys)
    // println(model.transform("percent"))

    model
  }
}
