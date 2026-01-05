from bluff import BluffController
from firstorderplayer import FirsOrderPlayer
from randomplayer import RandomBluffPlayer
from zeroorderplayer import ZeroOrderPlayer

controller = BluffController()
controller.join(RandomBluffPlayer())
controller.join(RandomBluffPlayer())
controller.play(debug=True)
print(controller.repeated_games(1000))
