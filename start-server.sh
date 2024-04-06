PID=$(pgrep -f "main.py")

if [ ! -z "$PID" ]; then
  echo "Server is running, PID: $PID. Restarting..."
  kill $PID
else
  echo "Server is not running. Starting..."
fi

nohup python3 main.py </dev/null >nohup.log 2>>error.log &

tail -f nohup.log | grep -m 1 "Shard ID None has connected to Gateway"
echo "Server started."
