-- The script goes into the CC:Tweaked computer
function log(msg)
  local time = os.epoch("local") / 1000
  local time_str = os.date("%Y-%m-%d %T", time)
  print(time_str.." "..msg)
end

function round(n)
  return math.floor(n+0.5)
end

log("Starting program")
bridge = peripheral.find("meBridge")

while true do  
  quantities = {}

  cat = bridge.listItems()
  if cat ~= nil then
    if type(cat) == "table" then
      for _, thing in pairs(cat) do
        strippedThing = { name = thing.name, amount = thing.amount, displayName = thing.displayName, type = "item" }
        table.insert(quantities, strippedThing)
      end
    else
      log("Error while processing AE:")
      log(cat)
    end
  end

  cat = bridge.listFluid()
  if cat ~= nil then
    if type(cat) == "table" then
      for _, thing in pairs(cat) do
        strippedThing = { name = thing.name, amount = round(thing.amount/1000), displayName = thing.displayName, type = "fluid" }
        table.insert(quantities, strippedThing)
      end
    else
      log("Error while processing AE:")
      log(cat)
    end
  end

  cat = bridge.listGas()
  if cat ~= nil then
    if type(cat) == "table" then
      for _, thing in pairs(cat) do
        strippedThing = { name = thing.name, amount = round(thing.amount/1000), displayName = thing.displayName, type = "gas" }
        table.insert(quantities, strippedThing)
      end
    else
      log("Error while processing AE:")
      log(cat)
    end
  end

  usageData = {
    items = {
      total = bridge.getTotalItemStorage(),
      used = bridge.getUsedItemStorage()
    },
    fluid = {
      total = bridge.getTotalFluidStorage(),
      used = bridge.getUsedFluidStorage()
    } -- no gas yet ):
  }

  allData = { usage = usageData, items = quantities }

  http.post("http://localhost:5000/ae2", textutils.serialiseJSON(allData), {["Content-Type"]= "application/json"})
  log("Request made. Now sleeping")
  sleep(5)
end