-- The script goes into the CC:Tweaked computer
function log(msg)
  local time = os.epoch("local") / 1000
  local time_str = os.date("%Y-%m-%d %T", time)
  print(time_str.." "..msg)
end

log("Starting program")
bridge = peripheral.find("meBridge")

while true do
  items = bridge.listItems()
  itemsData = {}

  for _, cat in pairs({ bridge.listItems(), bridge.listFluid(), bridge.listGas() }) do
    if cat ~= nil then
      if type(cat) == "table" then
        for _, item in pairs(cat) do
          strippedItem = { name = item.name, amount = item.amount, displayName = item.displayName }
          table.insert(itemsData, strippedItem)
        end
      else
        log("Error while processing AE:")
        log(cat)
      end
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

  allData = { usage = usageData, items = itemsData }

  http.post("http://localhost:5000/ae2", textutils.serialiseJSON(allData), {["Content-Type"]= "application/json"})
  log("Request made. Now sleeping")
  sleep(5)
end