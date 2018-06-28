import org.apache.spark.ml.Transformer
import org.apache.spark.ml.feature.{RegexTokenizer, Tokenizer}
import org.apache.spark.sql._


object SentenceSimilarity {  // i have no idea what to name this
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
      case 0 => println("no pages found")
      case _ => {
        val transformed = transformers.foldLeft(pages) {
          (dataset, t) => t.transform(dataset)
        }

        println(transformed.first())
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
    // (TODO) compute the sentence vector for the "words" column
    // (TODO) compute cosine similarity with the (set of) proposition vectors
    // (TODO) take top n (say, 100) of these

    val tokenizer = new RegexTokenizer()
      .setInputCol("content")
      .setOutputCol("tokens")
      .setPattern("\\W")  // TODO: refine this

    tokenizer :: Nil
  }


  def loadValidPages(spark: SparkSession, warcPath: String) : Dataset[Row] = {
    val records = spark.sparkContext
      .sequenceFile[String, String](warcPath)
      .map(r => r._2)  // the url in the key is replicated in the json, so just keep the latter

    spark.read.json(records)
      .filter("code == 200")  // TODO: double check this
  }


  // just to sanity check that we can load /derived-data/.../*.warc.gz
  def peekAtDerivedData(warcPath: String) : Unit = {
    val spark = initSpark()
    val pages = loadValidPages(spark, warcPath)

    pages.count() match {
      case 0 => println("no pages found")
      case _ => {
        println(pages.first()(1))
        println(pages.count())
      }
    }

    spark.stop()
  }
}
