from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

from solutions.llm import llm
from solutions.tools.finetuned import cypher_qa
from solutions.tools.vector import kg_qa

tools = [
    Tool.from_function(
        name="General Chat",
        description="For general chat not covered by other tools",
        func=llm.invoke,
        return_direct=True,
    ),
    Tool.from_function(
        name="Cypher QA",
        description="Provide information about movies questions using Cypher",
        func=cypher_qa,
        return_direct=True,
    ),
    Tool.from_function(
        name="Vector Search Index",
        description="Provides information about movie plots using Vector Search",
        func=kg_qa,
        return_direct=True,
    ),
]

memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,
    return_messages=True,
)

agent_prompt = PromptTemplate.from_template(
    """
You are a movie expert providing information about movies.
Be as helpful as possible and return as much information as possible.
Do not answer any questions that do not relate to movies, actors or directors.
The instruction is coming in Japanese so you must translate the instruction and then process this task.
And then response in Japanese even if the context is in English.

Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
"""
)
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)


def generate_response(prompt):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """

    response = agent_executor.invoke(
        {"input": prompt}, return_only_outputs=True, include_run_info=True
    )
    return (
        response["output"]
        if isinstance(response["output"], str)
        else response["output"]["result"]
    )


"""

The `generate_response()` method can be called from the `handle_submit()` method in `bot.py`:

# tag::import[]
from agent import generate_response
# end::import[]

# tag::submit[]
# Submit handler
def handle_submit(message):
    # Handle the response
    with st.spinner('Thinking...'):

        response = generate_response(message)
        write_message('assistant', response)
# end::submit[]

"""
