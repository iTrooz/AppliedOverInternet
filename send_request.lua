-- The script goes into the CC:Tweaked computer
print("Starting program")
bridge = peripheral.find("meBridge")

while true do
  items = bridge.listItems()
  itemsSemiJson = {}

  for _, cat in pairs({ bridge.listItems(), bridge.listFluid(), bridge.listGas() }) do
    if cat ~= nil then
      for _, item in pairs(cat) do
        strippedItem = { name = item.name, amount = item.amount, displayName = item.displayName }
        table.insert(itemsSemiJson, textutils.serialiseJSON(strippedItem)) -- for some reason I can't insert a table, I have to serialise it
      end
    end
  end
 
  itemsJsonStr = string.format("[%s]", table.concat(itemsSemiJson, ","))
  http.post("http://localhost:5000", itemsJsonStr)

  print("Request made. Now sleeping")
  sleep(5)
end
