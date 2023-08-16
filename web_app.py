import re
import requests
from bs4 import BeautifulSoup
import openai
import json
import random
import pandas as pd
from collections import Counter
from nltk.corpus import stopwords
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
nltk.download('stopwords')
from streamlit_option_menu import option_menu
nltk.download('stopwords')
openai.api_key="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"

def get_reviews(prod):
    base_URL = 'https://www.flipkart.com/search?q=' 
    prod = prod.replace(" ","")
    url = base_URL + prod
    req = requests.get(url)
    content = BeautifulSoup(req.content, 'html.parser')
    data = content.find('div', {'class':'_2kHMtA'})
    url_1 = 'https://www.flipkart.com'
    url_2 = data.find('a')['href']
    final_url = url_1 + url_2
    final_url = final_url.replace('/p/','/product-reviews/')
    final_url = final_url.split('FLIPKART')[0]
    final_url = final_url + 'FLIPKART'
    
    response = requests.get(final_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        target_div = soup.find('div', class_='_2MImiq _1Qnn1K')
        pattern = r'<span>(.*?)<\/span>'
        match = re.search(pattern, str(target_div))
        pages2 = match.group(1)
        page = int(pages2.split('of')[1])
    
    all_comments = []
    all_ratings = []
    
    for i in range(1, 7):#page + 1):
        new_url = f'{final_url}&page={i}'
        response = requests.get(new_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_elements = soup.find_all('div', class_='t-ZTKy')
            
            comments = [div_element.get_text(strip=True).split('READ MORE')[0] if div_element.get_text(strip=True) else 'No review available' for div_element in div_elements]
            all_comments.extend(comments)
            
            ratings = [div_element.get_text(strip=True) if div_element.get_text(strip=True) else 'NaN' for div_element in soup.find_all('div', class_='_3LWZlK _1BLPMq')]
            all_ratings.extend(ratings)
            
    return all_comments, all_ratings

def get_pos_senti(comments):
    msg = f"With utmost care, identify only the positive sentiment in the reviews and return them"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": msg},
        {"role": "assistant", "content": "Sure! Please provide me with the list of reviews."},
        {"role": "user", "content": str(comments)},
        {"role": "user", "content": "While returning Please stick to the following instructions"},
        {"role": "user", "content": "1. Return only the reviews"},
        {"role": "user", "content": "2. Dont add any extra words like Assistant:"},
        {"role": "user", "content": "3. While returning the reviews\ seperate each review by a comma"},
    ]
    response = openai.Completion.create(
        engine="text-davinci-003",  # Choose the appropriate engine
        prompt="\n".join([f"{message['role']}: {message['content']}" for message in messages]),
        max_tokens=2500  # Adjust the max_tokens as needed
    )
    review = response['choices'][0]['text']
    return review

def get_neg_senti(comments):
    msg = f"With utmost care, identify only the negative sentiment in the reviews and return them"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": msg},
        {"role": "assistant", "content": "Sure! Please provide me with the list of reviews."},
        {"role": "user", "content": str(comments)},
        {"role": "user", "content": "While returning Please stick to the following instructions"},
        {"role": "user", "content": "1. Return only the reviews"},
        {"role": "user", "content": "2. Dont add any extra words like Assistant:"},
        {"role": "user", "content": "3. While returning the reviews\ seperate each review by a comma"},
    ]
    response2 = openai.Completion.create(
        engine="text-davinci-003",  # Choose the appropriate engine
        prompt="\n".join([f"{message['role']}: {message['content']}" for message in messages]),
        max_tokens=2500  # Adjust the max_tokens as needed
    )
    review2 = response2['choices'][0]['text']
    return review2

def get_pos_neg_things(reviews):
    msg = f"You will be supplied with list containing positive and negative reviews about a product\
    Your task is to return 2 paragraphs seperated by a new line\ "
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": msg},
        {"role": "assistant", "content": "Sure! Please provide me with the list of reviews."},
        {"role": "user", "content": str(reviews)},
        {"role": "user", "content": "While returning the result\Please stick to the following instructions"},
        {"role": "user", "content": "1. Dont insert role conversation like - Assitant:Sure! in the final result, just return the paragrpraphs that i asked for"},
        {"role": "user", "content": "2. Using positive reviews frame sentences summarizing the positive reviews into a medium sized parapraph and name the heading of the paragraph as : Features buyers loved"},
        {"role": "user", "content": "3. Using negative reviews frame sentences summarizing the negative reviews into a small sized parapraph and name the heading of the paragraph as : Features that require improvement"},
        
    ]
    response2 = openai.Completion.create(
        engine="text-davinci-003", 
        prompt="\n".join([f"{message['role']}: {message['content']}" for message in messages]),
        max_tokens=2500)
    both_qual = response2['choices'][0]['text']
    return both_qual

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    col101, col102, col103 = st.columns([50,200,50])
    with col102:
           st.markdown("""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                    .custom-text { font-family: 'Agdasima', sans-serif; font-size: 50px;color:cyan }
                    </style>
                    <p class="custom-text">Sentiment analysis of a product using LLM </p>
                    """, unsafe_allow_html=True)
    st.write('')
    st.write('')
    selected = option_menu(None, ["About the project","Sentiment analysis","Developer contact details"], 
    icons=['pencil-square', "plus-slash-minus",  'file-person-fill'], menu_icon="cast", default_index=0, orientation="horizontal")
    
    if selected == 'About the project':
        st.subheader(':orange[About the project]')
        st.markdown('<div style="text-align: justify"> Flipkart remains a prominent player in India\'s online retail sector. Founded in 2007 by Sachin Bansal and Binny Bansal, the platform offers diverse products across categories like electronics, fashion, home essentials, and books. Renowned for its intuitive interface and customer-centric approach, Flipkart has revolutionized the shopping landscape. Notable features include Cash on Delivery, EMI options, and insightful customer reviews. Its annual sales events, including the Big Billion Days, provide substantial discounts. Flipkart has expanded into private label products, grocery delivery, and digital payments. With a focus on convenience, affordability, and customer satisfaction, Flipkart continues to shape India\'s e-commerce landscape. </div>', unsafe_allow_html=True)
        st.write('')
        st.markdown('<div style="text-align: justify"> Web scraping is a technique used to extract data from websites. It involves using automated tools to gather information from web pages, which can then be used for analysis, research, or other purposes. Web scraping involves sending requests to a website, parsing the HTML content, and extracting specific data elements such as text, images, links, and more. It\'s commonly employed by businesses, researchers, and developers to gather insights, monitor trends, and automate data collection processes. However, web scraping should be conducted responsibly and in compliance with the website\'s terms of use and legal regulations.</div>', unsafe_allow_html=True)
        st.write('')
        st.markdown('<div style="text-align: justify"> Sentiment analysis plays a pivotal role in the e-commerce sector by providing businesses with crucial insights into customer opinions and preferences. By analyzing customer reviews, comments, and social media interactions, businesses can gain a comprehensive understanding of how their products and services are perceived in the market. Positive sentiments can highlight successful aspects of offerings, while negative sentiments pinpoint areas for improvement. This information empowers companies to enhance their products, tailor marketing strategies, and improve customer experiences. Sentiment analysis also aids in real-time monitoring of brand reputation, allowing businesses to promptly address issues and maintain a positive online presence. Overall, sentiment analysis in e-commerce enables data-driven decision-making, leading to better products, increased customer satisfaction, and a stronger competitive edge.</div>', unsafe_allow_html=True)
        st.write('')
        st.markdown('<div style="text-align: justify"> ChatGPT can be instrumental in sentiment analysis by quickly analyzing text and determining the emotional tone expressed within it. By processing user input, it can accurately classify whether the sentiment is positive, negative, or neutral. This capability is valuable for businesses to gauge customer opinions, track social media sentiment, and understand public perception. ChatGPT\'s natural language understanding and generation skills enable it to interpret and respond to user queries, making sentiment analysis more accessible and efficient. It can assist in automating the process of extracting valuable insights from large volumes of text, saving time and effort in manual analysis.</div>', unsafe_allow_html=True)
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.divider()
        col1001, col1002, col1003,col1004, col1005 = st.columns([10,10,10,10,15])
        with col1005:
            st.markdown("""
                                <style>
                                @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                                .custom-text-10 { font-family: 'Agdasima', sans-serif; font-size: 28px;color: #ec7063  }
                                </style>
                                <p class="custom-text-10">An Effort by : _MAVERICK_GR_</p>
                                """, unsafe_allow_html=True)  


    if selected == 'Sentiment analysis':
        global comments
        comments = []
        st.write('')
        st.write('')
        product = st.text_input("Enter any product of your choice available for sale with Flipkart:","Type here")       
        st.error('Please make sure the product is avaiable for sale with Flipkart, otherwise you will get the response for the product which flikart supplies as alternative..', icon="🚨")
        st.write('')
        st.write('')
        if st.button(f'Fetch the buyer reviews for {product}.....',use_container_width=True,key=1):
            comments, ratings = get_reviews(product)
            random.shuffle(comments)
            st.success(f'Buyer reviews for the {product} fetched successfully from Flipkart website...', icon="✅")     
            st.write('')
            st.write('')
            st.success('Passing the fetched reviews to ChatGPT-3.5 for it to classify them as Positive or Negative')
            st.write('')
            st.write('')
            col001,col002 = st.columns([10,10])
            with col001:
                st.markdown("""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                    .custom-text-4 { font-family: 'Agdasima', sans-serif; font-size: 30px;color: #82e0aa  }
                    </style>
                    <p class="custom-text-4">Displaying the positive reviews </p>
                    """, unsafe_allow_html=True)
                positive_reviews = get_pos_senti(comments)
                reviews = positive_reviews.replace('-','')
                list_rev = reviews.split(',')
                df = pd.DataFrame(list_rev)
                df_cleaned = df[df[0].str.strip() != '']
                pattern = r'Assistant: \w+'
                mask = df_cleaned[0].str.contains(pattern)
                df_pos = df_cleaned.loc[~mask]
                df_pos.rename(columns={0:'Positive reviews'}, inplace=True)
                st.table(df_pos)
            with col002:
                st.markdown("""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                    .custom-text-5 { font-family: 'Agdasima', sans-serif; font-size: 30px;color:#e74c3c}
                    </style>
                    <p class="custom-text-5">Displaying the negative reviews </p>
                    """, unsafe_allow_html=True)
                negative_reviews = get_neg_senti(comments)
                reviews2 = negative_reviews.replace('-','')
                list_rev2 = reviews2.split(',')
                df2 = pd.DataFrame(list_rev2)
                df_cleaned2 = df2[df2[0].str.strip() != '']
                pattern = r'Assistant: \w+'
                mask = df_cleaned2[0].str.contains(pattern)
                df_neg = df_cleaned2.loc[~mask]
                df_neg.rename(columns={0:'Negative reviews'}, inplace=True)
                st.table(df_neg)
            st.write('')
            st.write('')
            st.success('Creating a wordcloud out of most frequent words in positive and negative reviews')
            st.write('')
            st.write('')
            col003,col004 = st.columns([10,10],gap="medium")
            with col003:
                st.markdown("""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                    .custom-text-7 { font-family: 'Agdasima', sans-serif; font-size: 30px;color: #229954 }
                    </style>
                    <p class="custom-text-7">Most frequent words in Positive reviews</p>
                    """, unsafe_allow_html=True)
                st.write('')
                st.write('')
                all_pos = ' '.join(df_pos['Positive reviews'])
                stop_words = set(stopwords.words('english'))
                words = re.findall(r'\w+', all_pos.lower())
                additional_stop_words = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9','10'
                                        '11','12','13','14','15','16','17','18','19','20','21','22','23','24','25'}
                all_stop_words = stop_words.union(additional_stop_words)
                filtered_words = [word for word in words if word not in all_stop_words]
                word_counts = Counter(filtered_words)
                top_n = 20
                top_words = word_counts.most_common(top_n)
                words_only = [word for word, _ in top_words]
                text = ' '.join(words_only)
                wordcloud = WordCloud(width=800, height=800, background_color='black').generate(text)
                st.image(wordcloud.to_array(),use_column_width=True)
            with col004:
                st.markdown("""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                    .custom-text-8 { font-family: 'Agdasima', sans-serif; font-size: 30px;color: #e74c3c }
                    </style>
                    <p class="custom-text-8">Most frequent words in Negative reviews</p>
                    """, unsafe_allow_html=True)
                st.write('')
                st.write('')
                all_neg = ' '.join(df_neg['Negative reviews'])
                stop_words = set(stopwords.words('english'))
                words = re.findall(r'\w+', all_neg.lower())
                additional_stop_words = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9','10'
                                        '11','12','13','14','15','16','17','18','19','20','21','22','23','24','25'}
                all_stop_words = stop_words.union(additional_stop_words)
                filtered_words = [word for word in words if word not in all_stop_words]
                word_counts = Counter(filtered_words)
                top_n = 20
                top_words = word_counts.most_common(top_n)
                words_only = [word for word, _ in top_words]
                text = ' '.join(words_only)
                wordcloud = WordCloud(width=800, height=800, background_color='black').generate(text)
                st.image(wordcloud.to_array(),use_column_width=True)
            st.write('')
            st.write('') 
            st.markdown("""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                    .custom-text-9 { font-family: 'Agdasima', sans-serif; font-size: 30px;color: #f4d03f }
                    </style>
                    <p class="custom-text-9">Summarizing the positive and negative reviews using ChatGPT-3.5 </p>
                    """, unsafe_allow_html=True)
            st.write('')   
            st.write('')   
            qualities = get_pos_neg_things(all_pos+all_neg)
            st.write(qualities)
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.divider()
        col1001, col1002, col1003,col1004, col1005 = st.columns([10,10,10,10,15])
        with col1005:
            st.markdown("""
                                <style>
                                @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                                .custom-text-11 { font-family: 'Agdasima', sans-serif; font-size: 28px;color:  #58d68d   }
                                </style>
                                <p class="custom-text-11">An Effort by : _MAVERICK_GR_</p>
                                """, unsafe_allow_html=True)  
            

    if selected == 'Developer contact details':
        st.divider()
        st.subheader(':orange[Developer contact details]')
        st.write('')
        st.write('')
        col301, col302 = st.columns([10,20])
        with col301:
            st.markdown(":orange[email id:]")
            st.write('')
        with col302:
            st.markdown(":yellow[gururaj008@gmail.com]")
            st.write('')

        col301, col302 = st.columns([10,20])
        with col301:
            st.markdown(":orange[Personal webpage hosting Datascience projects :]")
            st.write('')
        with col302:
            st.markdown(":yellow[https://gururaj-hc-personal-webpage.streamlit.app/]")
            st.write('')

        col301, col302 = st.columns([10,20])
        with col301:
            st.markdown(":orange[LinkedIn profile :]")
            st.write('')
        with col302:
            st.markdown(":yellow[https://www.linkedin.com/in/gururaj-hc-data-science-enthusiast/]")
            st.write('')


        col301, col302 = st.columns([10,20])
        with col301:
            st.markdown(":orange[Github link:]")
            st.write('')
        with col302:
            st.markdown(":yellow[https://github.com/Gururaj008]")
            st.write('')

                
                
        st.divider()
        col1001, col1002, col1003,col1004, col1005 = st.columns([10,10,10,10,15])
        with col1005:
            st.markdown("""
                                    <style>
                                    @import url('https://fonts.googleapis.com/css2?family=Agdasima');
                                    .custom-text-10 { font-family: 'Agdasima', sans-serif; font-size: 28px;color:cyan }
                                    </style>
                                    <p class="custom-text-10">An Effort by : _MAVERICK_GR_</p>
                                    """, unsafe_allow_html=True)


                    