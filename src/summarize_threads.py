from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate
# from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema.document import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv
from praw import Reddit
import requests
import os
import json
import tweepy
import json
import gradio as gr

# RAG
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

def summarize_tweets():

    with open("tweet_data.txt", "r", encoding="utf-8") as tweet_data:
        data = json.load(tweet_data)

    llm = ChatGroq(model="llama3-70b-8192")

    map_prompt_template = """You are provided with twitter thread comments. Most of the comments are discussions related to problems and solutions users are facing. Creat a concise summary of all the solutions and suggestions and key points mentioned in the discussions. \\n ===Comments=== \\n {text}"""
    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])

    combine_prompt_template = """
    The following is a set of summaries:
    {text}
    Take these and distill it into a final, consolidated summary
    of the main themes.
    """
    combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])

    map_reduce_chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt,
        return_intermediate_steps=True,
    )

    res = []
    final = []
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=2500, chunk_overlap=125)
    for val in data:
        title = val.split('$$')[0]
        val = val.split('$$')[1]
        print(f"Lenght of Reddit Thread",len(val.split()))
        split_docs = text_splitter.create_documents([val])
        summary = map_reduce_chain.invoke(split_docs)
        res.append(summary["output_text"])
        final.append({'title': title, 'summary': summary["output_text"]})
    
    with open("summary.txt", "w", encoding="utf-8") as summary_file:
        json.dump(res, summary_file)

    return []

def display_text_list():
    text_list = summarize_tweets()
    updates=[]
    for i, item in enumerate(text_list):
        title = "### " + item['title']
        summary = "<b>Summary</b> - " + item['summary']
        updates.append(gr.Markdown(value=title))
        updates.append(gr.Markdown(value="---"))
        updates.append(gr.Markdown(value=summary))

    return updates