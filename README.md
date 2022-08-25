Use this App to convert Speech to Text & then extract keywords  to Search in document set to provide the answers.
==================================================================================================================

This repository contains code for a Natural Language Processing utility built using Django which converts a user's speech into text, extracts key phrases from the converted text, uses these phrases to perform a full text search on  documentations, and finally display the top search results to the user in a UI.

![Architecure]()

# Problem Statement
Sometimes, when connecting with the helpdesk/customer service representatives our customers may need to spend a long time on the call to get their issues resolved. This may happen due any to the following reasons from rep’s perspective:

* Not knowing the solution right off the hat
* Difficulty in searching for the right documents to look for the answers
* Time taken to find the exact solution from the relevant documentations
* The need to refer multiple documents at a time
* Trouble understanding the customer’s issue due to his accent or complexity of the query

This might lead to lower First Call Resolution (FCR) rate and higher Mean Time To Resolution (MTTR).

# Solution Description
This utility aims to provide real time assistance to customer service rep by scanning through relevant  documents and displaying the best answers/info to the customer’s queries in the quickest possible time. We have automated the search on  documentations based on the customer’s query by extracting the key phrases from the customer’s recording and displaying the highest ranked search results to the representative.

![Process]()

# How to Get Started
1) Install the required python libraries <br />
	*pip install -r requirements.txt*

2) Create Azure Cognitive Services Language Resource (Azure subscription is required) <br />
  Follow Microsoft's official documentation at *https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows*

3) Access your Keys and Endpoints in Azure <br />
  * In the Azure Portal, go to *Resource Management -> Keys* and Endpoint <br />
  * Copy the endpoint and any one of the two keys provided, and use them in *src -> views.py*

4) Create your own document repository (Optional) <br />
  * Go to *src -> static -> documents* <br />
  * Add or delete PDF files according to your choice <br />
  * **Note**: If document repository is modified, **uncomment lines 154 through 172** under driver_function() in *src -> views.py* file. This is to create a dataframe and BM25 search object out of the documents. Comment out the lines again after the required dataframe and BM25 object is saved.

5) Run the Django development server
  * *python manage.py runserver* <br />
  * Open *http://127.0.0.1:8000/* on your web browser

# Values Delivered by the Solution
* Decreases Time to Resolution (TTR) and increases the customer satisfaction.
* May prevent follow up calls or request escalations.
* Improvement of efficiency and productivity.
* Can reduce the training time for the call center/help desk /insurance info dept representatives.
* Helps representatives to provide only necessary information, thereby improving compliance.
* Saves the call data in the form of key phrases and sentiment analysis scores for future analytics or survey.

# Scope of Improvements
* Search algorithm (BM25) and Cognitive Analytics can be tuned to work with synonyms and similar words.
* Instead of searching through the local repository of pdfs, one improvement could be to maintain a Table in a Database that maps each document with its location and the summary of that document.
* Sentiment Analysis on the recorded calls which can be used to monitor customer satisfaction and Rep’s performance.
* Our current code does not record a conversation i.e. it will record only that user's voice on whose machine the code is being run.


