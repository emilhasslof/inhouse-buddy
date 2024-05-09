from utils import *

snuslan_id="123169301094989825"
wew_id="745215730592645221"
guild_id = wew_id

if path.exists(f"stats/{guild_id}.json"):


    stats = {}
    with open(f"stats/{guild_id}.json", "r") as file: 
        stats_json = "\n".join(file.readlines())
        stats = json.loads(stats_json)
                

        # add win, subtract loss
        #radiant = ["slyver123", "jakob7121", "cricket9584", "jockwe", "mandelmans"]
        #radiant = ["lackosia", "cricket9584", "moulbaert1", "slyver123", "roggan."]
        winners = ['.skiipa', 'ottosson7254', 'fault9', 'mandelmans', 'kingo.1337'] 
        losers = ['sku6808', 'jockwe', 'cricket9584', 'lackosia', 'slyver123']
        # subtract win, add loss
        #dire = ["kingo.1337", ".skiipa", "sku6808", "lackosia", "jointzart"] 
        #dire = [".skiipa", "sku6808", "deeeeer", "__hackerman", "jointzart"]


        '''
        subtract_win(players=winners, stats=stats)
        add_loss(players=winners, stats=stats)

        subtract_loss(players=losers, stats=stats)
        add_win(players=losers, stats=stats)
        '''


        # update score, winrate, rank
        calculate_stats(stats)

    # Overwrite json with new stats
    with open(f"stats/{guild_id}.json", "w") as file:
        stats_json = json.dumps(stats, indent=4)
        file.writelines(stats_json)
