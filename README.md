# senti_analysis_LLM

In this project leveraged the capabilities of an LLM (ChatGPT 3.5 to be specific) to perform the sentiment analysis.


Below are the steps I followed in the project,


1. Since Flipkart is one of the leading e-commerce company in India, chose to carry out the sentiment analysis for any product available for sale with them


2. Ask user to input a product of his choice( bearing in mind the product is available for sale with Flipkart, otherwise we end up receiving reviews for a product which Flipkart populates in their website)


3. Scrap Flipkart's website using conventional methods for reviews provided by the buyers on the product inputted by the user in step 2


4. Pass the reviews to an LLM . Here is where I spent a lot of time rewriting my prompt to make the LLM understand what I am passing as input and what exactly am I expecting as response


5. Displayed the positive and negative reviews


6. Displayed the most frequent words in positive and negative reviews using Wordcloud


7. Again harnessing the power of LLM summarized the positive and negative reviews to identify the key strengths and scope for improvement for the chosen product


please feel free to check out the web-app hosted online at : https://gururaj-hc-sentiment-analysis-llm.streamlit.app/
