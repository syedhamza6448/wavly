import time

class DwellManager:
    def __init__(self, dwell_time=0.8):
        self.dwell_time = dwell_time
        # Tracks how long each fingertip has been on a key
        # key = fingertip index, value = {key_label, start_time}
        self.dwell_state = {}

    def update(self, fingertip_id, key_label):
        """
        Call every frame with the key the fingertip is currently over.
        Returns the key_label if dwell time is reached, else None.
        """
        now = time.time()
        state = self.dwell_state.get(fingertip_id)

        if state and state['key'] == key_label:
            # Same key — check if dwell time reached
            elapsed = now - state['start']
            if elapsed >= self.dwell_time:
                # Reset so it doesn't fire repeatedly
                self.dwell_state.pop(fingertip_id, None)
                return key_label
        else:
            # New key or no key — reset timer
            if key_label:
                self.dwell_state[fingertip_id] = {
                    'key': key_label,
                    'start': now
                }
            else:
                self.dwell_state.pop(fingertip_id, None)

        return None

    def get_progress(self, fingertip_id):
        """
        Returns dwell progress 0.0 to 1.0 for a fingertip.
        Used to draw the fill indicator on the key.
        """
        state = self.dwell_state.get(fingertip_id)
        if not state:
            return 0.0
        elapsed = time.time() - state['start']
        return min(elapsed / self.dwell_time, 1.0)

    def clear(self, fingertip_id=None):
        """Clears dwell state for one or all fingertips."""
        if fingertip_id is not None:
            self.dwell_state.pop(fingertip_id, None)
        else:
            self.dwell_state.clear()