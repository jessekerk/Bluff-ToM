from bluff import BluffController
from firstorderplayer import FirstOrderPlayer
from randomplayer import RandomBluffPlayer
from zeroorderplayer import ZeroOrderPlayer
from secondorderplayer import SecondOrderPlayer

controller = BluffController()
controller.join(FirstOrderPlayer())
controller.join(SecondOrderPlayer())
controller.play(debug=True)
print(controller.repeated_games(1000))
