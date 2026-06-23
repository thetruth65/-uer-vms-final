export interface StateConfig {
  id: string;
  name: string;
  port: number;
  url: string;
}

export const ALL_STATES: StateConfig[] = [];

try {
  const cached = localStorage.getItem('vms_all_states');
  if (cached) {
    const parsed = JSON.parse(cached);
    ALL_STATES.push(...parsed);
  }
} catch (e) {
  console.error(e);
}

export const updateAllStates = (newStates: StateConfig[]) => {
  newStates.forEach(newState => {
    const existing = ALL_STATES.find(s => s.id === newState.id);
    if (!existing) {
      ALL_STATES.push(newState);
    } else {
      existing.name = newState.name;
      existing.url = newState.url;
      existing.port = newState.port;
    }
  });
  localStorage.setItem('vms_all_states', JSON.stringify(ALL_STATES));
};
