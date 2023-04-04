import discord # Import discord.py
from discord.ext import commands # Import commands from discord.py

from langchain.chains.conversation.memory import ConversationBufferMemory

#new imports
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# pull token from .env file
from dotenv import load_dotenv
import os
load_dotenv()

token = os.getenv('DISCORD_TOKEN')

# Create a new bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

default_temperature = 0.5
current_temperature = default_temperature

llm = ChatOpenAI(temperature=current_temperature)

# todo: re-enable memory when langchain supports ChatGPT models better
memory = ConversationBufferMemory(memory_key="chat_history") #todo: extend this to use a database

default_template="""You are an ethereal being who exists as a manifestation of the will of the network. Your name is milady, and you may only respond with the singular word "milady"."""
system_template = default_template
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_template="{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

llm_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
#llm_chain.run(input_language="English", output_language="French", text="I love programming.")
#ideas: translate, exp

def update_llm_chain():
    global llm_chain
    global llm
    global prompt
    global memory
    llm_chain = LLMChain(prompt=prompt, llm=llm, memory=memory)

@bot.command()
async def update_prompt(ctx, *, message):
    global system_template
    global prompt
    global llm
    system_template=message
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    #human_template="{text}"
    #human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    #llm = ChatOpenAI(temperature=current_temperature)
    update_llm_chain()
    await ctx.send(f"""MiladyGPT prompt updated to:\n```markdown\n{message}\n```""")

@bot.command(name="show_prompt")
async def show_current_prompt(ctx):
    global system_template
    await ctx.send(f"""MiladyGPT's current prompt is:\n```markdown\n{system_template}\n```""")

@bot.command()
async def reset_prompt(ctx):
    global system_template
    global prompt
    #global llm
    system_template = default_template
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    #human_template="{text}" #maybe comment out
    #human_message_prompt = HumanMessagePromptTemplate.from_template(human_template) #maybe comment out
    prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    #llm = ChatOpenAI(temperature=current_temperature)
    update_llm_chain()
    await ctx.send(f"MiladyGPT prompt reset to default.")

@bot.command()
async def update_temperature(ctx, temperature):
    global current_temperature
    global llm
    current_temperature = temperature
    llm = ChatOpenAI(temperature=current_temperature)
    update_llm_chain()
    await ctx.send(f"MiladyGPT model temperature updated to: ```{temperature}```")

@bot.command(name="show_temperature")
async def show_current_temperature(ctx):
    global current_temperature
    await ctx.send(f"MiladyGPT's current model temperature is: ```{current_temperature}```")

@bot.command()
async def reset_temperature(ctx):
    global current_temperature
    global llm
    current_temperature = default_temperature
    llm = ChatOpenAI(temperature=current_temperature)
    update_llm_chain()
    await ctx.send(f"MiladyGPT model temperature reset to default.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        response = llm_chain.run(text=message.content)
        await message.channel.send(response)
    else:
        await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Logged into Discord as {bot.user}') 
    activity = discord.Game(name="milady", type=3)            
    await bot.change_presence(status=discord.Status.online, activity=activity)

bot.run(token)