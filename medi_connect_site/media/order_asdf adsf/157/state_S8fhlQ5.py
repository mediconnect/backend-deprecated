class State:
    def __init__(self):
        # True -> next state if see, False -> next state if not see
        self.next_state = dict()
        self.robot = None

    async def update(self):
        pass

    def str(self):
        pass


class Search(State):
    def update(self):
        pass


class Trans(State):
    async def update(self):
        await self.beep()
        return self.change()

    def change(self):
        print('Exiting: ' + self.str())
        state = self.next_state[True]
        print('Entering: ' + state.str())
        return state

    async def beep(self):
        text = 'state change'
        await self.robot.say_text(text, voice_pitch=5, duration_scalar=0.3).wait_for_completed()

    def str(self):
        return 'transition state'


class Track(State):
    def update(self):
        pass


class Start(State):
    def update(self):
        pass
