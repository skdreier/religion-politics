lazy val commonSettings = Seq(
    scalaVersion := "2.11.8",  // the version on workbench
    version      := "0.1",

    libraryDependencies ++= Seq(
      // the version on workbench; mark as provided b/c we're running this
      // through spark-submit.
      "org.apache.spark" %% "spark-core" % "2.1.1" % "provided",
      "org.apache.spark" %% "spark-mllib" % "2.1.1" % "provided",
      "org.apache.spark" %% "spark-sql" % "2.1.1" % "provided"
    )
)


// https://stackoverflow.com/questions/48540824/how-to-write-a-sbt-file-in-multiple-projects


lazy val root = (project in file("."))
  .settings(commonSettings)
  .aggregate(similarity)


lazy val similarity = project
  .settings(
    name := "SentenceSimilarity",
    mainClass in assembly := Some("relpol.similarity.SentenceSimilarity"),
    assemblyJarName in assembly := "sentencesimilarity.jar"
  )
  .settings(commonSettings: _*)


lazy val wv2parquet = project
  .settings(
    name := "WordVectorsToParquet",
    mainClass in assembly := Some("relpol.wv2parquet.Main"),
    assemblyJarName in assembly := "wv2parquet.jar",

    libraryDependencies ++= Seq(
      "org.json4s" %% "json4s-jackson" % "3.5.4",
      "commons-io" % "commons-io" % "2.6"
    )
  )
  .settings(commonSettings: _*)
