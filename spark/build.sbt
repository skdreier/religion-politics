lazy val root = (project in file(".")).
  settings(
    inThisBuild(List(
      scalaVersion := "2.11.8",  // the version on workbench
      version      := "0.1"
    )),
    name := "SentenceSimilarity",

    libraryDependencies ++= Seq(
      // the version on workbench; mark as provided b/c we're running this
      // through spark-submit.
      "org.apache.spark" %% "spark-core" % "2.1.1" % "provided",
      "org.apache.spark" %% "spark-mllib" % "2.1.1" % "provided",
      "org.apache.spark" %% "spark-sql" % "2.1.1" % "provided"
	)
  )
