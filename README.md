# CODENAME
This project was developed by me and a partner from university, the idea of the game is that there are two teams and in each one there is a special role called "Spymaster", who is available to see all agents in a small panel that is shown in his turn. This player must give his team a clue related to the words that are displayed downside each card. The team which asserts more agents wins. For more info about the game: https://en.wikipedia.org/wiki/Codenames_(board_game)

# Preview
![image](https://user-images.githubusercontent.com/79221793/131584663-d1e57c96-cbfb-41d5-8066-b319226a9eb9.png)

# Some Implementations
- Basic anticheat algorithm
  - If the algorithm detects that the players enter a word similar to a card word, it will penalize the team discounting points.
- Random words for each card
  - In each different game the program will show random words loaded in the dataset.txt
- Different consecuences depending on the selected agent
