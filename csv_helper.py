import csv

player_id_csv = "data/player_idlist.csv"
# dictionary will all the players and their IDs
player_id_dict = {}
with open(player_id_csv, mode='r', newline='') as file:
    csv_reader = csv.reader(file)
    # skip the first line
    next(csv_reader, None)
    for row in csv_reader:
        name = row[0] + " " + row[1]
        player_id_dict[name] = row[2]

# players can only be considered if they are a part of the first matchweek
players_set = set()

# CREATE THE PLAYERS CSV TO HAVE THESE MAPPINGS
players_input_path =  "data/fpl_players.csv"
players_output_path = "data/players.csv"
with open(players_input_path, mode='r', newline='') as infile, \
     open(players_output_path, mode='w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    header = next(reader)
    writer.writerow(['player_id'] + header) 
    for row in reader:
        player_name = row[0]
        players_set.add(player_name)
        new_row = [player_id_dict[player_name]] + row   
        writer.writerow(new_row)




# CREATE THE GAMEWEEK CSV TO HAVE THESE MAPPINGS
def insert_ids_csv(input_path, output_path, player_id_dict):
    with open(input_path, mode='r', newline='') as infile, \
        open(output_path, mode='w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        header = next(reader)
        writer.writerow(['player_id'] + header[1:]) 
        for row in reader:
            player_name = row[0]
            # should not consider players which join fpl late
            if player_name not in players_set:
                continue
            new_row = [player_id_dict[player_name]] + row[1:] 
            writer.writerow(new_row)
    
gw1_raw_path = "data/gw1-raw.csv"
gw1_output_path = "data/gw1.csv"
insert_ids_csv(gw1_raw_path, gw1_output_path, player_id_dict)

gw2_raw_path = "data/gw2-raw.csv"
gw2_output_path = "data/gw2.csv"
insert_ids_csv(gw2_raw_path, gw2_output_path, player_id_dict)


