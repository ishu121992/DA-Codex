import os
import openai
import pandas as pd
import sys
import io
import streamlit as st
import time

os.environ['OPENAI_API_KEY'] = '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'
openai.api_key = "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"

def csv_data_extractor(filepath):
    size = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    if size > 3000000:
        return 0
    else:
        try:
            df = pd.read_csv(filepath)
            df = replace_spaces_with_underscores(df)
            df.to_csv(filename,index=False)
            return df.columns.to_list(),filename,df.iloc[0,:]
        except:
            return f'Try uploading a csv file'

def replace_spaces_with_underscores(df):
    df.columns = df.columns.str.replace(' ', '_')
    return df

def fixed_prompt_portion(cols, filename):
    sent1 = 'Dataset has following columns: '
    sent2 = f'Dataset filename is {filename}'
    sent3 = 'Python 3'
    for i in cols:
        if cols.index(i) == len(cols)-1:
            sent1 = sent1[:-2]
        else:
            sent1 += (i + ', ')
    return sent1,sent2, sent3

def prompt_generator(sent1, sent2, data_sample, sent3, user_query):
    prefix_query ='Create a function to '
    prompt = f'"""{sent1}, {sent2}. Following is one row of the dataset: {data_sample}. #{sent3}. {prefix_query+user_query}."""'
    return prompt

def get_model_response(prompt):
    response = openai.Completion.create(
      model="code-davinci-002",
      prompt=prompt,
      temperature=0,
      max_tokens=500,
      top_p=1,
      frequency_penalty=0.2,
      presence_penalty=0
    )
    return response

def code_parser_input(code_list):
    output = ''
    for line in code_list:
        if len(line) == 0:
            output = output+'\n'
        elif '%' in line:
            continue
        elif '#' in line:
            line = line[1:]
            output +=(line+'\n')
        else:
            output +=(line+'\n')
    return output

def parse_response(response):
    code_to_parse = response['choices'][0]['text']
    c = code_to_parse.split('\n')
    imp_statements = [line for line in c if 'import' in line]
    code_to_ex = [line for line in c if line.find('import')]
    code_input_string = code_parser_input(code_to_ex)
    return imp_statements,code_input_string

def save_code_to_file(code_input_string,imp_statements):
    with open('test1.py', 'w') as fp:
        pass

    with open('test1.py', 'w') as f:
        for line in imp_statements:
            f.write(line)
            f.write('\n')
        for code_line in code_input_string:
            f.write(code_line)
    os.chmod('test1.py', 0o755)

if __name__ == '__main__':

    st.title('DAcodex')
    st.subheader('A tool to generate and execute code for data analysis using natural language queries')
    st.write('Upload a csv file')
    #load path of csv file from user in streamlit
    uploaded_file = st.file_uploader("Choose a csv file", type="csv")

    if uploaded_file is not None:
        file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type}
        st.write(file_details)
        if os.path.exists("tempDir") == False:
            os.mkdir("tempDir")
        with open(os.path.join("tempDir",uploaded_file.name),"wb") as f: 
            f.write(uploaded_file.getbuffer())         
            st.success("Saved File!")
            uploaded_file_name = os.path.join("tempDir",uploaded_file.name)

    if uploaded_file is not None:
        cols,filename,row = csv_data_extractor(uploaded_file_name)
        data_sample = dict(zip(cols,row))
        sent1,sent2,sent3 = fixed_prompt_portion(cols,uploaded_file_name)
        user_query = st.text_input('Enter your query')
        if user_query != '':
            prompt = prompt_generator(sent1, sent2, data_sample, sent3, user_query)
            # st.write(prompt)
            response = get_model_response(prompt)
            # show a loading spinner while waiting for the model to respond and display code in streamlit web app
            with st.spinner('Wait for it...'):
                time.sleep(5)

            # st.write(response)
            imp_statements,code_input_string = parse_response(response)
            save_code_to_file(code_input_string,imp_statements)

            #load code from file and display in streamlit web app with syntax highlighting
            with open('test1.py', 'r') as f:
                code = f.read()
            st.code(code, language='python')

            # add a button to execute code and display output in streamlit web app
            if st.button('Execute'):
                exec(code)
                # show output of above execution in streamlit web app without sys.stdout
                sys.stdout = io.StringIO()
                exec(code)
                output = sys.stdout.getvalue()
                st.write(output)
                # display output as plot in streamlit web app
                if 'plt.show()' in code:
                    st.pyplot()