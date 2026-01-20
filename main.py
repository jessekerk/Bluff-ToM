from bluff import BluffController
from firstorderplayer import FirstOrderPlayer
from randomplayer import RandomBluffPlayer
from zeroorderplayer import ZeroOrderPlayer

controller = BluffController()
controller.join(FirstOrderPlayer())
controller.join(ZeroOrderPlayer())
controller.play(debug=True)
print(controller.repeated_games(1000))
