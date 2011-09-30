from twisted.internet import reactor, stdio
from twisted.conch.stdio import ConsoleManhole, runWithProtocol

import _pypac

class PacManhole(ConsoleManhole):
    namespace = {
        'up':    _pypac.up,
        'down':  _pypac.down,
        'left':  _pypac.left,
        'right': _pypac.right,
    }

if __name__ == '__main__':
    _pypac.runGame()
    runWithProtocol(PacManhole)
