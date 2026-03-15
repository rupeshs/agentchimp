# AgentChimp

AgentChimp is a simple, autonomous personal AI agent. I chose to build it from scratch instead of using existing AI agent frameworks, so I could have full control over its design, features, and behavior.

## ✨ Key Features

- 🧩 **Modular Architecture** – Plug in channels, tools, and skills.  
- 🤖 **LLM Integration** – Supports OpenAI API compatible LLM endpoints llama.cpp, Ollama, OpenRouter, OpenAI, Groq etc  
- 🧠 **Memory** – Short-term and preference memory.  
- 🔐 **Secure** – Enforces the Principle of Least Privilege, restricting commands, tools, and filesystem access to only what is necessary.
- 🛠 **Tools** – Custom tools with validation & execution logic.  
- ⚙️ **Configurable** – Easily configurable environment variables through .env file  
- 🎯 **Skills** – Extend with reusable agent skills.  
- ⏰ **Job Scheduling** – Cron-style task automation.  
- 🔔 **Reminders** – Set reminders & notifications.
- 📦 **Sandbox** - Run inside docker sandbox
- 🩺 **Agent health** - Simply ask “agent health” to view the agent’s current system status.

## Getting Started

1. Clone the repository.
2. Create a virtual environment: `python -m venv env`. 
3. Activate the environment and install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.sample` to `.env` and update with your settings.
5. Run the Agent Chimp: `python main.py`.
6. Default channel is CLI(Terminal), if you want to run Telegram channel either configure in .env file or run using
`python main.py --channel telegram`


## Sandbox
Run using docker sandbox

Step 1: Create a folder cd into it and run the  below command to create sandbox
`docker sandbox run shell`

Then run the sandbox 
`docker sandbox run shell-agentchimp-sandbox`

Finally install and use AgentChimp.

## Components
Agent Chimp has following components
- Channels
- LLM (Brain)
- Memory (Short term memory + long term preference memory)
- Tools
- Agent Skills + scripts

## LLM Providers

Supports all OpenAI compatible LLM API providers.
We have tested following providers please refer `env.sample` file
- OpenAI
- OpenRouter
- Ollama(local,Cloud)
- Llama.cpp
- Groq

## Channels
You can talk with AgentChimp using the following channels:
- TUI (Terminal)
- Telegram 

> To add new channel implement abstract_channel.py
## Tools

Agent chimp has following in built tools:
| Tool Name                   | Description                                                                                                             |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `activate_skill_tool` | This tool is used by agent to activate a skill automatically    |
| `shell_tool`                | Executes shell commands on the system and returns the command output, by default all commands are  blocked and you can enable using `ALLOWED_COMMANDS` configuration |
| `python_script_runner_tool` | Executes a Python script used by Agent Skills (uv based environment creation)    |
| `current_time_tool`         | Returns the current system date and time.                                                                               |
| `search_tavily_tool`    | Perform web search using Tavily(Optional)
| `search_duckduckgo_tool`    | Performs a web search using DuckDuckGo and returns relevant search results.(NO API KEY)                                             |
| `list_files_tool`            | List files in a directory.                                                     |
| `read_file_tool`            | Reads the contents of a file from the workspace or specified path.                                                      |
| `write_file_tool`           | Writes content to a file(Inside workspace output folder) and creates the file if it does not exist.                                                     |
| `cron_tool`                 | Creates a new cron job to execute a task at a specified schedule. For example send me  top 5 AI news every morning 8 am                                                       |
| `list_cron_tool`            | Lists all scheduled cron jobs currently registered in the scheduler.                                                    |
| `delete_cron_tool`          | Deletes a specific cron job from the scheduler using its job ID.                                                        |
| `scheduler_tool`            | Schedules a task or job in the system scheduler with configurable timing or triggers.                                   |
| `system_health_tool`        | Provides system health information such as CPU usage, memory usage, disk status, and uptime.                            |


>To add a new tool, implement the `AbstractTool` class and place your implementation inside the `tools` directory. After restarting AgentChimp, the tool will be automatically discovered and loaded.
Recommended tool naming convention is
`<action>_<resource>_tool.py`
`e.g read_file_tool.py`

## Skills

Agent chimp supports agent skills.
The following skills available. 
| Skill Name           | Purpose                              | Example Query |
|----------------------|--------------------------------------|---------------|
| weather              | Retrieve current weather and forecast for a location(wttr.in) | "Weather in Kochi today" |
| currency-converter   | Convert money between currencies using latest exchange rates| "Convert 100 USD to INR" |

>Basic guide about [agent skills](https://nolowiz.com/agent-skills-complete-beginners-guide-to-ai-agent-skills-and-best-practices/)
You can create custom skills and place it inside `workspace/skills` folder.


## Telegram Bot Setup Guide

This guide explains how to create a Telegram bot and obtain the bot token required to interact with the Telegram API.

#### Create a Bot Using BotFather

Telegram provides an official bot creation tool called **BotFather**.

Follow these steps:

1. Open Telegram.
2. Search for **BotFather**.
3. Start a chat with BotFather.
4. Send the command: `/start`
5. Create a new bot: `/newbot`
6. Name your bot
7. Get the Bot Token paste it inside .env file
8. Start Agent Chimp and get your Telegram pairing code
9. Open your bot in telegram and send
 `/pair <pairing_code>`
10. After pairing you can now chat with Agent Chimp

## Contributing

Contributions are welcome! Please open issues for bugs or feature requests, and submit pull requests for enhancements.

## License

This project is licensed under the MIT License.