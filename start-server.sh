# Get the PID of the running server
PID=$(pgrep -f "main.py")

# If the server is running, kill it
if [ ! -z "$PID" ]; then
  echo "Server is running, PID: $PID. Restarting..."
  kill $PID
else
  echo "Server is not running. Starting..."
fi

# Start the server with a unique argument
nohup python3 main.py </dev/null &> nohup.log &
# Wait for the "Logged in as" message
tail -f nohup.log | grep -m 1 "Logged in as"
echo "Server started."
