if [ -f ".env.jims" ]; then
  if [ -f ".env.mine" ]; then
    echo "You have both .env.jims and .env.mine files. Please correct."
  else
    echo "Swapping .env.jims with .env.mine"
    mv .env .env.mine
    mv .env.jims .env
  fi
elif [ -f ".env.mine" ]; then
  if [ -f ".env.jims" ]; then
    echo "You have both .env.jims and .env.mine files. Please correct."
  else
    echo "Swapping .env.mine with .env.jims"
    mv .env .env.jims
    mv .env.mine .env
  fi
else
  echo "No .env.jims or .env.mine files found."
fi