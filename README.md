# inhouse-buddy

Discord bot to keep track of Dota 2 inhouse matches

Invite to your server: https://discord.com/api/oauth2/authorize?client_id=1065134684616536114&permissions=11005930512&scope=bot%20applications.commands

Use the /inhouse command in discord to prepare a match. The bot will create voice channels for each team.
Populate the channels with 5 players each and press "Lock Teams & Start" to begin the match.
When finished playing, tell the bot who won by pressing the corresponding button. Statistics will now be updated

Use the /inhouse-stats to show stats

Once teams are locked and match has begun, only certain users are allowed to report who won or cancel the match:

1. Players from either team
2. Members of the server with the role "Inhouse Manager". You need to create this role yourself to make use of this feature
3. Server admins
