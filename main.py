from bluff import BluffController
from firstorderplayer import FirstOrderPlayer
from randomplayer import RandomBluffPlayer
from zeroorderplayer import ZeroOrderPlayer

controller = BluffController()
controller.join(ZeroOrderPlayer())
controller.join(FirstOrderPlayer())
controller.play(debug=False)
print(controller.repeated_games(100))
