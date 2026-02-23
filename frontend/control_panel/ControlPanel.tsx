'use client';
import { useSimStore } from '../state_store/store';

export default function ControlPanel() {
  const replayMode = useSimStore((s) => s.replayMode);
  const setReplayMode = useSimStore((s) => s.setReplayMode);
  return (
    <div>
      <h3>Control Panel</h3>
      <label>
        <input type='checkbox' checked={replayMode} onChange={(e) => setReplayMode(e.target.checked)} /> Replay Mode
      </label>
    </div>
  );
}
