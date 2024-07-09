
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
#our custom crew ai tool
from tools import scrape_linkedin_posts_tool
from tools import scrape_single_linkedin_post_tool

import streamlit as st
import fitz# PyMuPDF
import os
from dotenv import load_dotenv
#Load environment
load_dotenv() # take environment variables from .env.
os.environ["OPENAI_API_KEY"]= os.getenv("OPENAI_API_KEY")


#to read data from pdf_file and return the object
def extract_text_from_pdf(pdf_file):
    # Open the PDF file
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    # Iterate through each page and extract text
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text


#Streamlit Framework
st.title("AI Assisted LinkedIn Post Generator")
#Form opening
with st.form(key='my-form'):
    #PDF Uploader
    organization_name = st.text_input("Enter your Orgnanization or Individuals name: ")
    #Example Post
    organization_context = st.text_area("What is your story or what is your org about, summarize: ")
    #Inspired Post
    org_or_person= st.radio(
        "Are you an Organization or an individual?",["Organization","Individual"]
    )
    
        
    organization_username = st.text_input("Pass linkedIn username to get the posts for example: ")
    print(f"organization_username: {organization_username!r}")
    #Generate Button
    col1,col2 = st.columns(2)
    with col1:
        emotional_appeal= st.selectbox(
            "What is the emotional appeal for the post: ",
            ("Inspiration", "Empathy", "Surprise", "Pride", "Humour"))
    with col2:
        type_of_post= st.selectbox(
            "Select the type of post: ",
            ("Text only Post", "Event Post", "NewsLetter Post", "Job Post", "Product Post","Thought Leadership Post",
             "Company News Post","Ask me anything Post","Reaction Post","Comparision Post","Behind the Scene Post","Quote Post"))
    
    emotional_appeal_post = st.text_input("Pass the link to a post which emulates a similar emotional appeal ")
    topic_of_interest= st.text_area("What do you want to talk about?")
    target_audience= st.text_area("Who are your target audience?")
    generate_button = st.form_submit_button("Generate")

if generate_button:
    if 'vector' not in st.session_state:
        st.session_state.embeddings = OpenAIEmbeddings()
    if org_or_person=="Organization":
        example_posts=scrape_linkedin_posts_tool.run({"profile": organization_username,"orglink": 1})
    else:
        example_posts=scrape_linkedin_posts_tool.run({"profile": organization_username,"orglink":0})

    reference_post = scrape_single_linkedin_post_tool.run({"link":emotional_appeal_post})
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    prompt = ChatPromptTemplate.from_template(
        """
Generate a professional, human-like LinkedIn post for {organizationname} about {topicofinterest}. This post should be tailored for {targetaudience} and formatted as a {typeofpost}.

CRITICAL: Your primary goal is to meticulously emulate the style, structure, tone, and impact of the reference post. Do not copy specific content, but recreate the essence of the reference post's writing style.

Additional Style Guidance:
While the reference post should be your primary guide for structure and overall approach, also consider this example post for additional stylistic inspiration:
{examplepost}

Analyze this example post for:
1. Tone and voice specific to {organizationname}
2. Any unique stylistic elements that could enhance your post
3. Industry-specific language or terms that might be relevant
Incorporate appropriate elements from this example post to further refine your writing style, ensuring it aligns with both the reference post's structure and {organizationname}'s voice.

Reference Post Analysis:
Carefully analyze the following reference post:
{referencepost}

Before crafting your post, explicitly state your findings on each of these elements:

a) Writing Style and Voice:
   - Identify the overall tone (e.g., formal, conversational, authoritative)
   - Note the level of industry-specific language or jargon used
   - Observe the balance between personal and professional language

b) Structure and Flow:
   - Analyze the post's organization (e.g., problem-solution, narrative, list-based)
   - Note the pacing and rhythm created by sentence and paragraph lengths
   - Identify any recurring patterns or structures used

c) Engagement Techniques:
   - List specific methods used to capture and maintain reader interest
   - Note any use of questions, challenges, or calls for reader input
   - Identify how the post encourages further engagement or action

d) Professional Authenticity:
   - Observe how the author establishes credibility and expertise
   - Note any personal anecdotes or experiences shared professionally
   - Identify elements that make the post feel genuinely human-written

After completing this analysis, craft your post by carefully integrating these elements:

1. Adopt the same overall tone and perspective throughout your writing
2. Mirror the structure and flow of the reference post
3. Incorporate similar engagement techniques to maintain reader interest
4. Emulate the level of professional authenticity present in the reference post

Your goal is to create a post that, if placed alongside the reference, would be indistinguishable in style and impact, while featuring entirely original content relevant to {topicofinterest} and {organizationname}.

Organizational Context:
{context}

Post Requirements:
1. Length: Match the reference post's length as closely as possible
2. Include hashtags only if present in the reference post, and in a similar manner
3. Strictly adhere to the provided organizational context and topic of interest

Content Guidelines:
1. Opening: Begin with a hook that mirrors the style and energy of the reference post
2. Body: Develop ideas following a similar flow and depth as the reference
3. Conclusion: End with a statement or question that echoes the reference post's closing strategy
4. Call-to-Action: Include only if present in the reference post, and in a similar style

Style and Tone Guidelines:
1. Write in a professional, human-like manner that could believably come from an industry expert
2. Avoid any elements not present in the reference post (e.g., emojis, excessive formatting)
3. Use industry-specific language only to the extent it's used in the reference post

Audience Targeting:
Adapt the content and language for {targetaudience}, considering their professional perspective and interests.

Additional Guidelines:
1. Proofread meticulously to eliminate any errors that would detract from the professional tone
2. Ensure all information aligns with the given organizational context and topic of interest

Restrictions:
1. Do not copy specific content from the reference post
2. Avoid including any information outside the given organizational context
3. Do not deviate from {topicofinterest}
4. Refrain from using any stylistic elements not present in the reference post

If the generated content does not closely emulate the reference post or seems inauthentic, please regenerate the post.
"""

    )


    #Test successful till here
    #Everything until this point is good. Now figure out how i can use that input Example and create a customized chain
    output_parser = StrOutputParser()
    chain = (
    {
        "organizationname": (lambda x: organization_name),
        "topicofinterest": (lambda x: topic_of_interest),
        "targetaudience": (lambda x: target_audience),
        "typeofpost": (lambda x: type_of_post),
        "context": (lambda x: organization_context),
        "emotionalappeal": (lambda x: emotional_appeal),
        "examplepost": (lambda x: example_posts),
        "referencepost": (lambda x: x),
    }
    |prompt
    | llm
    | output_parser
    )
    st.write(chain.invoke({"referencepost":reference_post}))
    