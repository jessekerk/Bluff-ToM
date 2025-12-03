from zeroorderplayer import ZeroOrderPlayer
from firstorderplayer import FirsOrderPlayer
from bluff import Bluff

game = Bluff()
game.join(FirsOrderPlayer) # type: ignore
game.join(ZeroOrderPlayer) # type: ignore
game.play(debug=True)
print(game.repeated_games(1000))