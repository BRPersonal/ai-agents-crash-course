# ai-agents-crash-course
Examples from Udemy course - AI Agents Crash Course

$ conda create -n ai-agent python=3.13 -y
$ conda activate ai-agent
(ai-agent) $ pip install -r requirements.txt
(ai-agent) $ pip install notebook

Add the following entries to your .env
OPENAI_API_KEY=your-api-key
OPENAI_DEFAULT_MODEL=your-model

Setting up PyCharm 
---------- 
OPen the project folder in pyCharm. It will say Python interpreter is not configured. 
Click on configure click on add interpreter, click on add local , select "Existing" tab" and then naviage to 
the folder /Applications/anaconda3/envs/ai-agent/bin/python and click ok. 
Now open a terminal and you should see virtual environment activated prompt like this
(ai-agent) $


Running code samples
--------------
#1)
simplest_agent.py

#2)
tool_calling.py

#3)
rag_calories_data_setup.py
rag_nutrients_qa_data_setup.py

#4)
rag.py

