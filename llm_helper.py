import re
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.llm import LLMChain
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.prompts import PromptTemplate
from langchain.chat_models import AzureChatOpenAI

from langchain.embeddings import AzureOpenAIEmbeddings

from vector_storage import init_vector_store
from customprompt import PROMPT


class LLMHelper:
    # LLMHelper is a class that helps to use the LLM model to answer questions and extract followup questions
    # from the answer. It also helps to get the context of the answer from the source documents.
    # The class is initialized with a custom prompt that can be used to customize the answer.
    # The class can be used in two ways:
    # 1. To answer a question and extract followup questions from the answer
    # 2. To answer a question and get the context of the answer from the source documents

    def __init__(self, custom_prompt="", temperature=0.7):
        # Initialize the LLM model
        # TODO: Change to use open source LLM model
        self.llm = AzureChatOpenAI(
            azure_deployment="AskSenacor-gpt35turbo-v1",
            openai_api_version="2023-05-15",
            temperature=temperature,
        )
        # Initialize the prompt - this can be customized
        self.prompt = PROMPT if custom_prompt == '' else PromptTemplate(template=custom_prompt,
                                                                        input_variables=["summaries", "question"])

        self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment="AskSenacor-ada002-v1",
                openai_api_version="2023-05-15",
            )
        # Initialize the vector store, which is used to store and retrieve the source documents
        self.vector_store = init_vector_store(
            embeddings=self.embeddings,
            index_name="langchain-vector-demo")

    def extract_followupquestions(self, answer):
        # Extract followup questions from the answer, this is an optional feature
        followupTag = answer.find('Follow-up Questions')
        followupQuestions = answer.find('<<')

        # take min of followupTag and folloupQuestions if not -1 to avoid taking the followup questions if there is
        # no followupTag
        followupTag = min(followupTag, followupQuestions) if followupTag != -1 and followupQuestions != -1 else max(
            followupTag, followupQuestions)
        answer_without_followupquestions = answer[:followupTag] if followupTag != -1 else answer
        followup_questions = answer[followupTag:].strip() if followupTag != -1 else ''

        # Extract the followup questions as a list
        pattern = r'\<\<(.*?)\>\>'
        match = re.search(pattern, followup_questions)
        followup_questions_list = []
        while match:
            followup_questions_list.append(followup_questions[match.start() + 2:match.end() - 2])
            followup_questions = followup_questions[match.end():]
            match = re.search(pattern, followup_questions)

        if followup_questions_list != '':
            # Extract follow up question
            pattern = r'\d. (.*)'
            match = re.search(pattern, followup_questions)
            while match:
                followup_questions_list.append(followup_questions[match.start() + 3:match.end()])
                followup_questions = followup_questions[match.end():]
                match = re.search(pattern, followup_questions)

        if followup_questions_list != '':
            pattern = r'Follow-up Question: (.*)'
            match = re.search(pattern, followup_questions)
            while match:
                followup_questions_list.append(followup_questions[match.start() + 19:match.end()])
                followup_questions = followup_questions[match.end():]
                match = re.search(pattern, followup_questions)

        # Special case when 'Follow-up questions:' appears in the answer after the <<
        followupTag = answer_without_followupquestions.lower().find('follow-up questions')
        if followupTag != -1:
            answer_without_followupquestions = answer_without_followupquestions[:followupTag]
        followupTag = answer_without_followupquestions.lower().find('follow up questions')  # LLM can make variations...
        if followupTag != -1:
            answer_without_followupquestions = answer_without_followupquestions[:followupTag]

        return answer_without_followupquestions, followup_questions_list

    def get_semantic_answer_lang_chain(self, question, chat_history):
        # Get the answer from the LLM model including the sources, and takes chat history into account
        question_generator = LLMChain(llm=self.llm, prompt=CONDENSE_QUESTION_PROMPT, verbose=False)
        doc_chain = load_qa_with_sources_chain(self.llm, chain_type="stuff", verbose=False, prompt=self.prompt)
        # TODO: Add a more sophisticated retrieval chain
        chain = ConversationalRetrievalChain(
            retriever=self.vector_store.as_retriever(),
            question_generator=question_generator,
            combine_docs_chain=doc_chain,
            return_source_documents=True,
            # top_k_docs_for_context= self.k
        )
        result = chain({"question": question, "chat_history": chat_history})
        sources = "\n".join(set(map(lambda x: x.metadata["source"], result['source_documents'])))

        contextDict = {}
        for res in result['source_documents']:
            source_key = self.filter_sources_links(res.metadata['source']).replace('\n', '').replace(' ', '')
            if source_key not in contextDict:
                contextDict[source_key] = []
            myPageContent = self.clean_encoding(res.page_content)
            contextDict[source_key].append(myPageContent)

        result['answer'] = \
            result['answer'].split('SOURCES:')[0].split('Sources:')[0].split('SOURCE:')[0].split('Source:')[0]
        result['answer'] = self.clean_encoding(result['answer'])
        sources = self.filter_sources_links(sources)

        return question, result['answer'], contextDict, sources

    # Simple QA
    def standard_query(self, question, k=3, model_name="gpt-3.5-turbo"):
        # Create a retriever from the Chroma vector database
        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        # Create a RetrievalQA from the model and retriever
        qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=retriever)
        return qa(question)

    def insert_citations_in_answer(self, answer, filenameList):
        # Insert citations in the answer to indicate the source of the answer
        filenameList_lowered = [x.lower() for x in filenameList]    # LLM can make case mitakes in returing the filename of the source

        matched_sources = []
        pattern = r'\[\[(.*?)\]\]'
        match = re.search(pattern, answer)
        while match:
            filename = match.group(1).split('.')[0] # remove any extension to the name of the source document
            if filename in filenameList:
                if filename not in matched_sources:
                    matched_sources.append(filename.lower())
                filenameIndex = filenameList.index(filename) + 1
                answer = answer[:match.start()] + '$^{' + f'{filenameIndex}' + '}$' + answer[match.end():]
            else:
                answer = answer[:match.start()] + '$^{' + f'{filename.lower()}' + '}$' + answer[match.end():]
            match = re.search(pattern, answer)

        # When page is reloaded search for references already added to the answer (e.g. '${(id+1)}')
        for id, filename in enumerate(filenameList_lowered):
            reference = '$^{' + f'{id+1}' + '}$'
            if reference in answer and not filename in matched_sources:
                matched_sources.append(filename)

        return answer, matched_sources, filenameList_lowered

    def get_links_filenames(self, answer, sources):
        # Get the links and filenames of the source documents
        split_sources = sources.split('  \n ')
        srcList = []
        for src in split_sources:
            if src != '':
                srcList.append(src)
        return answer, srcList

    def print_semantic_similarity(self, question, k=3, search_type="similarity"):
        # Can be used to test the semantic search function of the vector store
        docs = self.vector_store.similarity_search(
            query=question,
            k=k,
            search_type=search_type,
        )
        print(docs[0].page_content)


    @staticmethod
    def clean_encoding(text):
        # Clean the encoding of the text
        try:
            encoding = 'ISO-8859-1'
            encodedtext = text.encode(encoding)
            encodedtext = encodedtext.decode('utf-8')
        except Exception as e:
            encodedtext = text
        return encodedtext

    @staticmethod
    def filter_sources_links(sources):
        # use regex to replace all occurences of '[anypath/anypath/somefilename.xxx](the_link)' to '[somefilename](
        # thelink)' in sources
        pattern = r'\[[^\]]*?/([^/\]]*?)\]'

        match = re.search(pattern, sources)
        while match:
            withoutExtensions = match.group(1).split('.')[0]  # remove any extension to the name of the source document
            sources = sources[:match.start()] + f'[{withoutExtensions}]' + sources[match.end():]
            match = re.search(pattern, sources)

        sources = '  \n ' + sources.replace('\n', '  \n ')  # add a carriage return after each source
        return sources
