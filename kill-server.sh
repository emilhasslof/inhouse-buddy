# Get the PID of the running server
PID=$(pgrep -f "main.py")

# If the server is running, kill it
if [ ! -z "$PID" ]; then
  echo "Server is running, PID: $PID. Killing..."
  kill $PID
else
  echo "No running server found"
fi
