package relpol.similarity

import org.apache.spark.ml.UnaryTransformer
import org.apache.spark.ml.feature.Word2VecModel
import org.apache.spark.ml.linalg.{Vector, DenseVector}
import org.apache.spark.ml.linalg.SQLDataTypes.VectorType
import org.apache.spark.ml.param.Param
import org.apache.spark.ml.util.{DefaultParamsReadable, DefaultParamsWritable, Identifiable}
import org.apache.spark.mllib.feature
import org.apache.spark.sql.types.DataType


class SentenceVectorizer (override val uid: String)
  extends UnaryTransformer[Seq[String], Vector, SentenceVectorizer]
  with DefaultParamsWritable {

    // (TODO) compute the sentence vector for the "words" column
    //     https://stackoverflow.com/questions/43866703/load-word2vec-model-in-spark
    //     https://github.com/apache/spark/blob/v2.1.1/mllib/src/main/scala/org/apache/spark/ml/feature/ElementwiseProduct.scala
    //     https://github.com/acharneski/ImageLabs/blob/blog-2017-10-07/src/main/scala/interactive/word2vec/SparkLab.scala#L310

  def this() = this(Identifiable.randomUID("sentVec"))

  val vectorMap: Param[Word2VecModel] = new Param(this, "vectorMap", "word vector mapping")
  def setVectorMap(value: Word2VecModel): this.type = set(vectorMap, value)
  def getVectorMap(): Word2VecModel = getOrDefault(vectorMap)

  override protected def createTransformFunc: Seq[String] => Vector = {
	//require(params.contains(vectorMap), s"word vector map required")
	arr => new DenseVector(new Array[Double](1))  // TODO: not this, obviously
  }

  override protected def outputDataType: DataType = VectorType
}
