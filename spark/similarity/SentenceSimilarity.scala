package relpol.similarity

import org.apache.spark.ml.Transformer
import org.apache.spark.ml.feature.RegexTokenizer
import org.apache.spark.ml.feature.Word2VecModel
import org.apache.spark.sql._


object SentenceSimilarity {
  def main(args: Array[String]) : Unit = {
    args match {
      case Array(action, warcPath, _*) => {
        action match {
          case "run" => run(warcPath)
          case "sanity" => peekAtDerivedData(warcPath)
          case _ => println("Invalid action provided")
        }
      }
      case _ => println("Expected at least 2 arguments (action, path to .warc.gz)")
    }
  }


  def run(warcPath: String) : Unit = {
    val spark = initSpark()
    val transformers = initTransformers()
    val pages = loadValidPages(spark, warcPath)

    pages.count() match {
      case 0 => println("No pages found")
      case _ => {
        val transformed = transformers.foldLeft(pages) {
          (dataset, t) => t.transform(dataset)
        }

        // for now, just print what the hell we're doing
        println(transformed.first)
      }
    }

    spark.stop()
  }


  def initSpark() : SparkSession = {
    SparkSession.builder()
      .appName("SentenceSimilarity")
      .getOrCreate()
  }


  def initTransformers() : List[Transformer] = {
    // operations:
    // (DONE, ish) tokenize the "content" column -> "words" column
    //     maybe replace with spark-nlp tokenizer, which handles sentences properly
    // (TODO) take top n (say, 100) of these

    val tokenizer = new RegexTokenizer()
      .setInputCol("content")
      .setOutputCol("tokens")
      .setPattern("\\W")  // TODO: refine this

    // val vectorMap = loadWordVectors(file)
    val vectorizer = new SentenceVectorizer()
      .setInputCol("tokens")
      .setOutputCol("vectors")
      //.setVectorMap(vectorMap)

    // val similarity = new BatchCosineSimilarity()
    //   .setInputCol("vectors")
    //   .setOutputCol("similarity")

    tokenizer :: vectorizer :: Nil
  }


  def loadValidPages(spark: SparkSession, warcPath: String) : Dataset[Row] = {
    val records = spark.sparkContext
      .sequenceFile[String, String](warcPath)
      .map(r => r._2)  // the url in the key is replicated in the json, so just keep the latter

    spark.read.json(records)
      .filter("code == 200")  // TODO: double check this; perhaps also filter on mime-type?
  }


  // just to sanity check that we can load /dataset-derived/.../*.warc.gz
  def peekAtDerivedData(warcPath: String) : Unit = {
    val spark = initSpark()
    val pages = loadValidPages(spark, warcPath)

    pages.count() match {
      case 0 => println("No pages found")
      case _ => {
        println(pages.first(1))
        println(pages.count)
      }
    }

    spark.stop()
  }
}
