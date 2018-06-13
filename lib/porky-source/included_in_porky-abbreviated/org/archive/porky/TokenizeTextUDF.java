/*
 * Copyright 2013 Internet Archive
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you
 * may not use this file except in compliance with the License. You
 * may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
 * implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */


package org.archive.porky;

import java.io.IOException;
import org.apache.pig.EvalFunc;
import org.apache.pig.data.Tuple;
import org.apache.pig.impl.util.WrappedIOException;
import java.util.regex.*;
import java.io.*;
import java.net.*;
import org.apache.pig.PigException;
import org.apache.pig.backend.executionengine.ExecException;
import org.apache.pig.data.TupleFactory;
import org.apache.pig.data.DataBag;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import java.util.ArrayList;
import java.util.List;
import java.util.Iterator;
import org.apache.lucene.analysis.*;
import org.apache.lucene.analysis.tokenattributes.*;
//import org.apache.lucene.analysis.util.*;
import org.apache.lucene.util.*;
import org.apache.lucene.analysis.standard.*;
//import org.apache.lucene.analysis.core.*;
import org.apache.lucene.analysis.*;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.lang.Integer;

/**
 * UDF which reads in a text string, and returns a tokenized string (removing stop words and punctuation)
 */ 

public class TokenizeTextUDF extends EvalFunc<String> {
	
  String stopWordsFile;
  CharArraySet stopSet = null;

  public TokenizeTextUDF(String file) {
  	stopWordsFile = file;
  }

  public String exec(Tuple input) throws IOException {

	String emptyString = "";
	if(input == null || input.size() == 0) {
		return emptyString;
	}
	try {
		String textString = (String)input.get(0);
		if(textString == null) {
			return emptyString;
		}
		if(stopSet == null) {
			//initialize
			List<String> stopWords = new ArrayList<String>();
			//read in stop words file
			// Open the file as a local file.
			FileReader fr = new FileReader(stopWordsFile);
			BufferedReader d = new BufferedReader(fr);
			String line;
			while ((line = d.readLine()) != null) {
				stopWords.add(line);
			}
			fr.close();
			stopSet = new CharArraySet(stopWords, true);
		}
	
		StandardTokenizer tokenStream = new StandardTokenizer(AttributeFactory.DEFAULT_ATTRIBUTE_FACTORY);
		tokenStream.setReader(new StringReader(textString));
		tokenStream.reset();
		TokenStream tokenStream2 = new StopFilter(tokenStream, stopSet);
		StringBuilder sb = new StringBuilder();
		CharTermAttribute charTermAttribute = tokenStream2.addAttribute(CharTermAttribute.class);
		tokenStream2.reset();
		while (tokenStream2.incrementToken()) {
			String term = charTermAttribute.toString();
			sb.append(term + " ");
		}
		return sb.toString();

	} catch(Exception e){
                return emptyString;
        }
  }
}
